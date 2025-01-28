import os
from dotenv import load_dotenv
import psycopg2
import ollama
import sys
load_dotenv()
sys.path.append("sessions")
sys.path.append("messages")
sys.path.append("users")
from sessions import get_sessions_list, get_session
from messages import add_message
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
        for (title, doc, link) in dbcursor1:
            results.append([str(title), str(doc), str(link)])
    dbconn.commit()
    dbcursor1.close()    
    dbcursor.fetchall()
    return(results)

def get_pages_for_answer(prompt, session_id, dbconn):
    dbcursor = dbconn.cursor()
    message_id = add_message(session_id, "user", prompt, dbconn)
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

def askllm(prompt, dbconn, session_id = 1) -> str:
    # RAG
    pages = get_pages_for_answer(prompt, session_id, dbconn)
    # Add RAG pages for messages from history
    for history_page in get_pages_for_history(session_id, dbconn):
        if history_page not in pages:
            pages.append(history_page)
    resultstr = str()
    for (title, data, link) in pages:
        resultstr += "Title: {}\nData: {}\nLink: {}\n".format(title, data, link)
    # print(resultstr)
    ##Get history
    # session_messages = get_session(session_id, dbconn)
    # print("History:\n{}\n".format(session_messages))
    ##Send question    
    output = ollama.generate(
        model="llama3.2",
        prompt=f"""You are Marvin bot from The Hitchhiker's Guide to the Galaxy.
                Using this data: {resultstr}.
                Respond to this prompt: {prompt}.
                Make short and clear answers, respond concisely and use emojis."""
        )
#                ("Use this history of our last conversation: {history}." if len(history) > 5 else "") +
                
#                Show the links to data after your answer after the word 'Links:'."""
#                And at the end of answer  after the word "History:" write short history of our conversation for our next conversation."""
#        )

#    answer = output['response'].split("History:")
#    print("New history:\n{0}\n\n".format(answer[1]))
#    if (len(history) > 0):
#        query = "UPDATE history SET history=%s WHERE id=%s"
#    else:
#        query = "INSERT INTO history (history, id) VALUES (%s, %s)"
#    data = (answer[1], session_id)
#    dbcursor.execute(query, data)
#    dbconn.commit()
#    return(answer)
    message_id = add_message(session_id, "assistant", output['response'], dbconn)
    return(output['response'])
##    return (output['response'])

# Connect to your postgres DB
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
)

curr_session_id = 0
sessions_list = get_sessions_list("test_user@42heilbronn.de", dbconn)
for session in sessions_list:
    curr_session_id = session[0]
    print("Session id {} title: {}, end_time: {}".format(session[0], session[1], session[2]))
    messages_list = get_session(session[0], dbconn)
    for message in messages_list:
        print("{} role {}: {}".format(message[0], message[1], message[2]))

print("Write your question:")
for prompt in sys.stdin:
    if (prompt.rstrip() == "exit"):
        break
    print("Answer from llama:\n{0}\n\n".format(askllm(prompt, dbconn, curr_session_id)))
    print("Write your question:")

print("Done")
