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

def get_messages(session_id, dbconn):
    dbcursor = dbconn.cursor()
    messages_list=list()
    query = ("""SELECT messages.role, messages.content, messages.id
            FROM messages, sessions
            WHERE messages.session_id = sessions.id AND sessions.id = %s
            ORDER BY messages.id ASC""")
    dbcursor.execute(query, (session_id, ))
    for (role, content, id) in dbcursor:        
        messages_list.append({'role': role, 'content': content})
##    print(messages_list)
    dbcursor.close()
    return(messages_list)
