import psycopg

def get_db_connection():
    return psycopg.connect(
        host="localhost",
        dbname="Sistema_Mantenimiento",
        user="postgres",
        password="1321",
        autocommit=True
    )
