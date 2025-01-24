import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
    )

def add_user(user_name):
    # Open a cursor to perform database operations
    dbcursor = dbconn.cursor()    
    query = ("""INSERT INTO users (login) VALUES(%s)""")
    dbcursor.execute(query, (user_name, ))
    dbconn.commit()
    dbcursor.close()
