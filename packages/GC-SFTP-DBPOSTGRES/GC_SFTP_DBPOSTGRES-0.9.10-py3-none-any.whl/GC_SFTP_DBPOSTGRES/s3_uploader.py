import boto3
import os
import pandas as pd
from datetime import datetime, timedelta
import configparser
from concurrent.futures import ThreadPoolExecutor, as_completed

def write_log(message, log_file):
    with open(log_file, 'a') as log:
        log.write(f"{datetime.now()} - {message}\n")

def create_main_folder(s3_folder, bucket_name, s3, log_file):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{s3_folder}/", Delimiter='/')
    if 'Contents' not in response:
        s3.put_object(Bucket=bucket_name, Key=f"{s3_folder}/")
        write_log(f"Carpeta principal creada en S3: s3://{bucket_name}/{s3_folder}/", log_file)
    else:
        write_log(f"La carpeta principal ya existe en S3: s3://{bucket_name}/{s3_folder}/", log_file)

def create_subfolder(s3_folder, subfolder, bucket_name, s3, log_file):
    s3_key = os.path.join(s3_folder, subfolder, '')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_key, Delimiter='/')
    if 'Contents' not in response:
        s3.put_object(Bucket=bucket_name, Key=s3_key)
        write_log(f"Subcarpeta creada en S3: s3://{bucket_name}/{s3_key}", log_file)
    else:
        write_log(f"La subcarpeta ya existe en S3: s3://{bucket_name}/{s3_key}", log_file)

def clean_old_logs(log_folder, log_file):
    cutoff_date = datetime.now() - timedelta(days=15)
    for log_file in os.listdir(log_folder):
        log_file_path = os.path.join(log_folder, log_file)
        if os.path.isfile(log_file_path) and log_file.endswith('.log'):
            file_date_str = log_file.replace('.log', '')
            try:
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                if file_date < cutoff_date:
                    os.remove(log_file_path)
                    write_log(f"Archivo de log antiguo eliminado: {log_file_path}", log_file)
            except ValueError:
                pass

def process_file(file_name, subfolder, s3_folder, source_folder, bucket_name, s3, log_file):
    if 'cleaned.parquet' in file_name:
        write_log(f"Archivo {file_name} omitido porque contiene 'cleaned.parquet'.", log_file)
        return

    csv_file_path = os.path.join(source_folder, subfolder, file_name)
    subfolder_name = file_name.split('-')[1].split('_')[0]  # Ajuste para remover el sufijo de fecha/hora
    create_subfolder(s3_folder, subfolder_name, bucket_name, s3, log_file)
    parquet_file_name = file_name.replace('.csv', '.parquet')
    parquet_file_path = os.path.join(source_folder, subfolder, parquet_file_name)
    s3_key = os.path.join(s3_folder, subfolder_name, parquet_file_name)

    try:
        df = pd.read_csv(csv_file_path, low_memory=False)
        
        # Segunda validación antes de guardar y subir el archivo Parquet
        if 'cleaned.parquet' not in parquet_file_name:
            df.to_parquet(parquet_file_path, index=False, engine='pyarrow')
            s3.upload_file(parquet_file_path, bucket_name, s3_key)
            write_log(f"El archivo {parquet_file_path} ha sido subido a s3://{bucket_name}/{s3_key}", log_file)
            os.remove(parquet_file_path)
        
        os.remove(csv_file_path)
        write_log(f"El archivo CSV original {csv_file_path} ha sido eliminado.", log_file)
    except Exception as e:
        write_log(f"Error al procesar el archivo {csv_file_path}: {e}", log_file)

# Esto debería estar en tu script app.py donde llamas a ejecutar_subida_s3
def ejecutar_subida_s3(config):
    source_folder = config['directorio_origen']
    log_folder = config['log_folder']
    log_file = os.path.join(log_folder, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    bucket_name = config['bucket_name']

    s3 = boto3.client('s3')
    folders = [f for f in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, f))]

    for folder in folders:
        folder_path = os.path.join(source_folder, folder)
        s3_folder = folder
        create_main_folder(s3_folder, bucket_name, s3, log_file)
        files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_file = {executor.submit(process_file, file, folder, s3_folder, source_folder, bucket_name, s3, log_file): file for file in files}
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    future.result()
                except Exception as e:
                    write_log(f"Error inesperado con el archivo {file}: {e}", log_file)
