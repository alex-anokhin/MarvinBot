import psycopg2

def add_user(user_name, dbconn):
    dbcursor = dbconn.cursor()    
    query = ("""INSERT INTO users (login) VALUES(%s)""")
    dbcursor.execute(query, (user_name, ))
    dbconn.commit()
    dbcursor.close()
