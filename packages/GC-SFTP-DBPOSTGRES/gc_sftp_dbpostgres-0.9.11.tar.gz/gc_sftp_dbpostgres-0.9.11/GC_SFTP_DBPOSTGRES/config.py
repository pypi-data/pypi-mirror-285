import configparser

def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    return {
        'bucket_name': config['DEFAULT']['bucket_name'],
        'directorio_origen': config['DEFAULT']['directorio_origen'],
        'log_folder': config['DEFAULT']['log_folder'],
        'db_host': config['DEFAULT']['db_host'],
        'db_port': config['DEFAULT']['db_port'],
        'db_user': config['DEFAULT']['db_user'],
        'db_password': config['DEFAULT']['db_password'],
        'db_name': config['DEFAULT']['db_name'],
        'directorio_local': config['DEFAULT']['directorio_local'],
    }
