from setuptools import setup, find_packages

setup(
    name='GC_SFTP_DBPOSTGRES',
    version='0.9.10',  # Actualiza la versión aquí
    packages=find_packages(),
    install_requires=[
        'boto3',
        'psycopg2-binary',
        'pandas',
        'configparser'
    ],
    description='Paquete para optimizar la carga y transferencia de datos a PostgreSQL y S3',
    long_description="""
    La función carga_datos_efficient está diseñada para optimizar el proceso de carga de datos mediante técnicas avanzadas de procesamiento paralelo. 
    Esta función mejora significativamente el rendimiento y la eficiencia en la gestión de grandes volúmenes de datos, asegurando una carga rápida y segura. 
    A continuación se detallan sus características principales:

    - Procesamiento Paralelo: Distribuye la carga de trabajo entre múltiples unidades de procesamiento para acelerar el tiempo de carga.
    - Robustez y Fiabilidad: Implementa mecanismos avanzados de control y recuperación de errores para mantener la integridad de los datos durante todo el proceso.
    - Escalabilidad: Permite ajustar los parámetros de carga para adaptarse a diferentes volúmenes de datos y capacidades del sistema.
    - Registro y Monitoreo: Proporciona registros detallados y en tiempo real del proceso de carga, facilitando el monitoreo, análisis y resolución de problemas.

    Esta función es ideal para escenarios donde se requiere una gestión eficiente de grandes conjuntos de datos, aprovechando al máximo los recursos del sistema.

    Parámetros:

    - ruta_archivo: La ruta del archivo de datos a cargar.
    - configuracion: Diccionario opcional con configuraciones adicionales para personalizar el comportamiento de la función, como el nivel de detalle en los registros y las opciones de recuperación de errores.

    Retorno:

    - resultado: Un diccionario con el estado de la carga, incluyendo detalles sobre el éxito, posibles errores y estadísticas de rendimiento.
    """,
    long_description_content_type='text/markdown',
    author='Giancarlos Cardenas',
    author_email='gcardenas@bim.pe',
    url='https://github.com/tu_usuario/GC_SFTP_DBPOSTGRES',
)
