import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()





def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USERNAME'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port='5432'
    )
    return connection
