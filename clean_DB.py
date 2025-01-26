import os
from dotenv import load_dotenv
import psycopg2

## clean DB, but without embedded pages

load_dotenv()
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                                  dbname=os.getenv("DB_NAME"),
                                  user=os.getenv("DB_USER"),
                                  password=os.getenv("DB_PASSWORD")
)
dbcursor = dbconn.cursor()
query = ("DELETE FROM rag_for_messages")
dbcursor.execute(query)
query = ("DELETE FROM messages")
dbcursor.execute(query)
query = ("DELETE FROM sessions")
dbcursor.execute(query)
query = ("DELETE FROM users")
dbcursor.execute(query)
dbconn.commit()
dbcursor.close()
