import os
import psycopg2

import sys
sys.path.append("../users")
from users import add_user

def get_sessions_list(user_name, dbconn):
    dbcursor = dbconn.cursor()
    rowcnt=0
    sessions_list=list()
    while (rowcnt == 0):
        query = ("""SELECT sessions.id, sessions.title, sessions.end_time FROM sessions, users
                WHERE sessions.user_id = users.id AND users.login = %s""")
        dbcursor.execute(query, (user_name, ))
        rowcnt = dbcursor.rowcount
        if (dbcursor.rowcount == 0):
            add_user(user_name, dbconn)
    # dbconn.commit()
    for (session_id, title, end_time) in dbcursor:        
        sessions_list.append((session_id, title, end_time))
    dbcursor.close()
    return(sessions_list)

def get_session(session_id, dbconn):
    dbcursor = dbconn.cursor()
    messages_list=list()
    query = ("""SELECT messages.time, messages.role, messages.content
            FROM messages, sessions
            WHERE messages.session_id = sessions.id AND sessions.id = %s""")
    dbcursor.execute(query, (session_id, ))
    rowcnt = dbcursor.rowcount
    # dbconn.commit()
    for message in dbcursor:        
        messages_list.append(message)
    dbcursor.close()
    return(messages_list)

def create_new_session(user_name, dbconn):
    dbcursor = dbconn.cursor()    
    query = ("""INSERT INTO sessions (user_id, title)
            VALUES((SELECT id FROM users WHERE login = %s),
                'Last session')""")
    dbcursor.execute(query, (user_name, ))
    dbconn.commit()
    dbcursor.close()
