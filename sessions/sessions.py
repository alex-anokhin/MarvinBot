import os
from dotenv import load_dotenv
import psycopg2

import sys
sys.path.append("../users")
sys.path.append("../messages")
from users import add_user
from messages import add_message

# Load environment variables (need to create .env file with DB credentials)
load_dotenv()

# Connect to your postgres DB
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
)

def get_sessions_list(user_name):
    # Open a cursor to perform database operations
    dbcursor = dbconn.cursor()
    rowcnt=0
    sessions_list=list()
    while (rowcnt == 0):
        query = ("""SELECT sessions.id, sessions.title, sessions.end_time FROM sessions, users
                WHERE sessions.user_id = users.id AND users.login = %s""")
        dbcursor.execute(query, (user_name, ))
        rowcnt = dbcursor.rowcount
        if (dbcursor.rowcount == 0):
            add_user(user_name)
    # dbconn.commit()
    for (session_id, title, end_time) in dbcursor:        
        sessions_list.append((session_id, title, end_time))
    dbcursor.close()
    return(sessions_list)

def get_session(session_id):
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

def create_new_session(user_name):
    dbcursor = dbconn.cursor()    
    query = ("""INSERT INTO sessions (user_id, title)
            VALUES((SELECT id FROM users WHERE login = %s),
                'Last session')""")
    dbcursor.execute(query, (user_name, ))
    dbconn.commit()
    dbcursor.close()


#create_new_session("test_user1@42heilbronn.de") 
sessions_list = get_sessions_list("test_user@42heilbronn.de")
for session in sessions_list:
    print("Session id {} title: {}, end_time: {}".format(session[0], session[1], session[2]))
#    add_message(session[0], "usr", "Message")
    messages_list = get_session(session[0])
    for message in messages_list:
        print("{} role {}: {}".format(message[0], message[1], message[2]))
