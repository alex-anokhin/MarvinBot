import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables (need to create .env file with DB credentials)
load_dotenv()

# Connect to your postgres DB
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
)

def add_message(session_id, role, content):
    dbcursor = dbconn.cursor()    
    query = ("""INSERT INTO messages (session_id, role, content)
            VALUES(%s, %s, %s)""")
    dbcursor.execute(query, (session_id, role, content))
    dbconn.commit()
    dbcursor.close()
