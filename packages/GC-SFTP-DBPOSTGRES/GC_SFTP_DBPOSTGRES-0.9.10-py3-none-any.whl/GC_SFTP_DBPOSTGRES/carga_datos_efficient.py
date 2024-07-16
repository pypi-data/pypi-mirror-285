import os
import psycopg2
import configparser
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configuración de logging
log_dir = "logscript"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Generar el nombre del archivo de log basado en la fecha actual
log_filename = datetime.now().strftime('%Y-%m-%d.log')
log_filepath = os.path.join(log_dir, log_filename)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler()  # Agregar manejador de consola
    ]
)

def clean_old_logs(log_directory, days_to_keep=15):
    """ Elimina archivos de log más antiguos que el número especificado de días. """
    today = datetime.now()
    cutoff_date = today - timedelta(days_to_keep)
    files_removed = 0

    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        file_date_str = filename.split('.')[0]
        try:
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
            if file_date < cutoff_date:
                os.remove(file_path)
                files_removed += 1
                logging.info(f"Archivo de log antiguo eliminado: {filename}")
        except ValueError:
            logging.info(f"No se pudo analizar la fecha del archivo: {filename}")

    logging.info(f"Total de archivos de log limpiados: {files_removed}")

# Llamar a la función para eliminar logs antiguos
clean_old_logs(log_dir)

# Leer configuración desde config.ini
config = configparser.RawConfigParser()
config.read('config.ini')

# Datos de conexión desde el archivo config.ini
db_host = config['DEFAULT']['db_host']
db_port = config['DEFAULT']['db_port']
db_user = config['DEFAULT']['db_user']
db_password = config['DEFAULT']['db_password']
db_name = config['DEFAULT']['db_name']
directorio_local = config['DEFAULT']['directorio_local']

def obtener_columnas_tabla(schema, table_name, connection):
    query = f"""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = '{schema}' AND table_name = '{table_name}'
    """
    cursor = connection.cursor()
    cursor.execute(query)
    columns = cursor.fetchall()
    cursor.close()
    # Omitir las columnas FECHA_CARGA y FECHA_ACTUALIZACION
    return [col[0].upper() for col in columns if col[0].upper() not in ['FECHA_CARGA', 'FECHA_ACTUALIZACION']]

def validate_and_clean_csv(file_path, columnas_tabla, delimiter):
    try:
        df = pd.read_csv(file_path, delimiter=delimiter, dtype=str, decimal=',')  # Leer todos los datos como strings para conservar el formato original
    except pd.errors.ParserError as e:
        logging.error(f"Error al analizar el archivo {file_path}: {e}")
        raise

    # Validar y limpiar la columna 'ID' si existe, sino agregarla
    if 'ID' in df.columns:
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        df = df.dropna(subset=['ID'])
        df['ID'] = df['ID'].astype(int).astype(str)
    else:
        df['ID'] = None  # Agregar columna ID con valores nulos

    # Validar que no haya columnas faltantes
    for column in columnas_tabla:
        if column not in df.columns:
            df[column] = None  # Agregar columnas faltantes con valores nulos

    # Solo mantener las columnas que existen en la tabla
    df = df[[col for col in columnas_tabla if col in df.columns]]
    
    # Guardar el archivo limpio temporalmente
    cleaned_file_path = file_path.replace('.csv', '_cleaned.csv')
    df.to_csv(cleaned_file_path, index=False, sep=delimiter)
    return cleaned_file_path

def cargar_csv_a_postgres(file_path, schema, table_name):
    max_retries = 3
    attempt = 0
    success = False
    delimiter = '~'  # Usar el delimitador correcto

    while attempt < max_retries and not success:
        try:
            # Conexión a la base de datos
            connection = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                dbname=db_name
            )
            
            # Obtener las columnas de la tabla
            columnas_tabla = obtener_columnas_tabla(schema, table_name, connection)
            
            # Validar y limpiar el archivo CSV
            cleaned_file_path = validate_and_clean_csv(file_path, columnas_tabla, delimiter)
            
            # Leer el archivo CSV limpio y preparar el contenido para COPY
            with open(cleaned_file_path, 'r') as f:
                copy_sql = f"""
                COPY "{schema}"."{table_name}" ({', '.join(f'"{col}"' for col in columnas_tabla)}) 
                FROM STDIN WITH CSV HEADER
                DELIMITER AS '{delimiter}'
                """
                cursor = connection.cursor()
                cursor.copy_expert(sql=copy_sql, file=f)
                connection.commit()
                cursor.close()
                connection.close()
                logging.info(f"Datos cargados en {schema}.{table_name} desde {cleaned_file_path}")
                success = True
        except Exception as e:
            attempt += 1
            logging.error(f"Error al cargar datos desde {file_path} a {schema}.{table_name}: {e}")
            if attempt < max_retries:
                logging.info(f"Reintentando cargar el archivo {file_path} ({attempt}/{max_retries})")
            else:
                logging.error(f"Máximo número de intentos alcanzado para el archivo {file_path}")
            if connection:
                connection.close()

def contar_registros_db(schema, table_name):
    """ Cuenta el número de registros en la tabla de la base de datos. """
    try:
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()
        count_query = f'SELECT COUNT(*) FROM "{schema}"."{table_name}"'
        cursor.execute(count_query)
        num_records_db = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return num_records_db
    except Exception as e:
        logging.error(f"Error al contar registros en la base de datos: {e}")
        return None

def identificar_y_recargar_registros_faltantes(file_path, schema, table_name):
    """ Identifica y recarga los registros faltantes desde el archivo CSV original a la base de datos. """
    try:
        df = pd.read_csv(file_path, delimiter='~', decimal=',', dtype=str)  # Leer todos los datos como strings
        original_ids = set(df['ID'])
        
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
        cursor = connection.cursor()
        
        id_query = f'SELECT "ID" FROM "{schema}"."{table_name}"'
        cursor.execute(id_query)
        db_ids = set(record[0] for record in cursor.fetchall())
        
        missing_ids = original_ids - db_ids
        logging.info(f'IDs faltantes: {missing_ids}')
        
        if missing_ids:
            missing_records = df[df['ID'].isin(missing_ids)]
            
            for _, record in missing_records.iterrows():
                # Ajuste de valores que pueden estar fuera de rango
                record_dict = record.to_dict()

                insert_query = f"""
                INSERT INTO "{schema}"."{table_name}" 
                ({', '.join(f'"{col}"' for col in obtener_columnas_tabla(schema, table_name, connection))}) 
                VALUES ({', '.join(f'%({col})s' for col in obtener_columnas_tabla(schema, table_name, connection))})
                """
                cursor.execute(insert_query, record_dict)
            
            connection.commit()
            logging.info('Registros faltantes insertados correctamente.')
        
        cursor.close()
        connection.close()
    except Exception as e:
        logging.error(f"Error al identificar y recargar registros faltantes: {e}")

def procesar_archivos_en_directorio(directorio_base):
    for root, dirs, files in os.walk(directorio_base):
        # Omitir el directorio base y procesar solo subdirectorios
        if root == directorio_base:
            continue
        for filename in files:
            if filename.endswith(".csv"):
                try:
                    # Extraer el esquema y el nombre de la tabla del nombre del archivo
                    schema, table_part = filename.split('-')
                    table_name = '_'.join(table_part.rsplit('_', 1)[:-1])
                    # Ruta completa del archivo
                    file_path = os.path.join(root, filename)

                    # Intentar cargar los datos del archivo CSV en la tabla correspondiente
                    cargar_csv_a_postgres(file_path, schema, table_name)
                except Exception as e:
                    logging.error(f"Error al procesar el archivo {filename}: {e}")

try:
    # Procesar todos los archivos en los subdirectorios del directorio local
    procesar_archivos_en_directorio(directorio_local)

except Exception as error:
    logging.error(f"Error al conectar a la base de datos o cargar los datos: {error}")
