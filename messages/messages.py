import psycopg2

# role =
#   user
#   system
#   assistant

def add_message(session_id, role, content, dbconn):
    dbcursor = dbconn.cursor()    
    query = ("""INSERT INTO messages (session_id, role, content)
            VALUES(%s, %s, %s)
            RETURNING id""")
    dbcursor.execute(query, (session_id, role, content))
    message_id = 0
    for (mess_id) in dbcursor:
        message_id = mess_id
    dbconn.commit()
    dbcursor.close()
    return (message_id)

