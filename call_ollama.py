import os
from dotenv import load_dotenv
import psycopg2
import ollama
from ollama import chat
import sys
load_dotenv()
sys.path.append("sessions")
sys.path.append("messages")
sys.path.append("users")
from sessions import get_sessions_list, get_session
from messages import add_message, get_messages
from users import add_user

def get_pages_for_history(session_id, dbconn):
    dbcursor = dbconn.cursor()
    query = """SELECT DISTINCT ON (page_id) page_id FROM rag_for_messages, messages, sessions
            WHERE rag_for_messages.message_id=messages.id
                AND messages.session_id = sessions.id
                AND sessions.id = %s"""
    dbcursor.execute(query, (session_id,))
    results = list()
    dbcursor1 = dbconn.cursor()
    for (page_id) in dbcursor:
        query = ("""SELECT title, doc, link FROM pages WHERE id = %s""")
        dbcursor1.execute(query, (page_id,))
        for (title, data, link) in dbcursor1:
            results.append("Title: {}\nData: {}\nLink: {}\n".format(title, data, link))
    dbconn.commit()
    dbcursor1.close()    
    dbcursor.fetchall()
    dbcursor.close() 
    return(results)

def get_pages_for_answer(prompt, message_id, dbconn):
    dbcursor = dbconn.cursor()
    response = ollama.embeddings(
        prompt=prompt,
        model="mxbai-embed-large"
        )
    ##Get vectors
    query = "SELECT id, title, doc, link FROM pages ORDER BY embedding <=> %s LIMIT 3"
    ##print(str(response["embedding"]))
    data = ((str(response["embedding"])), )
    dbcursor.execute(query, data)
    results = list()
    dbcursor1 = dbconn.cursor()
    for (page_id, title, doc, link) in dbcursor:
        #print(""Result of SQL Select:" Title: {0}; Doc: {1}; Link: {2}".format(str(title), str(doc), str(link)))
        results.append([str(title), str(doc), str(link)])
        query = ("""INSERT INTO rag_for_messages (message_id, page_id)
            VALUES(%s, %s)""")
        dbcursor1.execute(query, (message_id, page_id))
    dbcursor.fetchall()
    dbconn.commit()
    dbcursor1.close()
    dbcursor.close()
    return(results)

def get_answer_from_ollama(prompt, dbconn, session_id = 1) -> str:
    # RAG
    message_id = add_message(session_id, "user", prompt, dbconn)
    pages = get_pages_for_answer(prompt, message_id, dbconn)
    # Add RAG for messages from history
    if (os.getenv("USE_RAG_HISTORY", "False") == "True"):
        history_pages = get_pages_for_history(session_id, dbconn)
        pages.append(history_pages)
##    for page in pages:
##        print(page)
##        print('\n')
##    Get message history
    session_messages = [{'role': 'system', 'content': f"""You are Marvin bot from The Hitchhiker's Guide to the Galaxy.
                        Using this data for answer:{pages}.
                        Make short and clear answers, respond concisely and use emojis."""}]
    session_messages.extend(get_messages(session_id, dbconn))
    response = chat(
        'llama3.2',
        messages = session_messages,
        options={'temperature': 0.75}
        )

##    message_id = add_message(session_id, "assistant", output['response'], dbconn)
    message_id = add_message(session_id, "assistant", response['message']['content'], dbconn)
    return(response['message']['content'])
##    return (output['response'])

# Connect to postgres DB
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
)

curr_session_id = 0
sessions_list = get_sessions_list("test_user@42heilbronn.de", dbconn)
for session in sessions_list:
    curr_session_id = session[0]
##    print("Session id {} title: {}, end_time: {}".format(session[0], session[1], session[2]))
##    messages_list = get_session(session[0], dbconn)
##    for message in messages_list:
##        print("{} role {}: {}".format(message[0], message[1], message[2]))

print("Write your question:")
for prompt in sys.stdin:
    if (prompt.rstrip() == "exit"):
        break
    print("Answer from llama:\n{0}\n\n".format(get_answer_from_ollama(prompt, dbconn, curr_session_id)))
    print("Write your question:")

print("Done")
