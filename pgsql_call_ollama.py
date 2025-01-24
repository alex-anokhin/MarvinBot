import os
from dotenv import load_dotenv
import psycopg2
import ollama

load_dotenv()
# Connect to your postgres DB
dbconn = psycopg2.connect(host=os.getenv("DB_HOST"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
)


# Open a cursor to perform database operations
dbcursor = dbconn.cursor()

def askllm(prompt, session_id = 1) -> str:
    response = ollama.embeddings(
        prompt=prompt,
        model="mxbai-embed-large"
        )
    ##Get vectors
    query = "SELECT title, doc, link FROM pages ORDER BY embedding <=> %s LIMIT 3"
    ##print(str(response["embedding"]))
    data = ((str(response["embedding"])), )
    dbcursor.execute(query, data)
    results = list()
    for (title, doc, link) in dbcursor:
        #print(""Result of SQL Select:" Title: {0}; Doc: {1}; Link: {2}".format(str(title), str(doc), str(link)))
        results.append([str(title), str(doc), str(link)])
    dbcursor.fetchall()
    resultstr = str()
    for (title, data, link) in results:
        resultstr += "Title: {0}\nData: {1}\nLink: {2}\n".format(title, data, link)
#    print(resultstr)

    ##Get history
#    history = str()
#    query = "SELECT history FROM history WHERE id=%s"
#    data = (session_id, )
#    dbcursor.execute(query, data)
#    for (historys,) in dbcursor:
#        history = historys
#    dbcursor.fetchall()
#    print("Previous history:\n{0}\n".format(history))
    ##Send question
#    answer = list()
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
    return(output['response'])
##    return (output['response'])

    
print("Write your question:")
import sys
#prompt = "How can I prepare me to Exam? Say me short."
##history = str()
for prompt in sys.stdin:
    if (prompt.rstrip() == "exit"):
        break
    print("Answer from llama:\n{0}\n\n".format(askllm(prompt)))
    print("Write your question:")

print("Done")
dbcursor.close()



