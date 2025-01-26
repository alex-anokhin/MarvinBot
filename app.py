import json
import re
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import requests
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import psycopg2
import ollama
from dotenv import load_dotenv
import os
from googlesearch import search
from bs4 import BeautifulSoup
# import src.pgsql_call_ollama as pgsql_call_ollama

# Load the .env file
load_dotenv()

OLLAMA_API = "http://localhost:11434/api/chat"

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Update with your frontend's URL
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all HTTP methods
#     allow_headers=["*"],  # Allow all headers
# )

app.mount("/static", StaticFiles(directory="static"), name="static")

# class data(BaseModel):
class Data(BaseModel):
	model: str
	messages: list
	stream: bool = False
	temperature: float = Field(0.75, ge=0.1, le=2)
	max_tokens: int = Field(256, ge=1, le=4096)
	top_p: float = Field(1.0, ge=0.1, le=1.0)

templates = Jinja2Templates(directory="templates")

# Connect to your postgres DB
dbconn = psycopg2.connect(
	host=os.getenv("DB_HOST"),
	dbname=os.getenv("DB_NAME"),
	user=os.getenv("DB_USER"),
	password=os.getenv("DB_PASSWORD")
)
# Open a cursor to perform database operations
dbcursor = dbconn.cursor()
def check_call(user_prompt):
	# Prepare the request payload
	payload = {
		"model": "llama3.1",
		"prompt": f"Define does user prompt require search in internal knowledgebase for answer:\n{user_prompt}\nRespond using JSON.",
		# "format": "json",
		"format": {
			"type": "object",
			"properties": {
			"requires_search": {
				"type": "boolean"
			}
			},
			"required": [
			"requires_search"
			]
		},
		"stream": False
	}

	# Send the request to the Ollama API
	response = requests.post("http://localhost:11434/api/generate", json=payload)

	# Check the response
	if response.status_code == 200:
		response_json = response.json()
		print("check_call:\n", response_json)
		# Assuming the response contains a field 'requires_search' that indicates if a search is needed
		response_data = response_json.get("response", "{}")
		response_dict = json.loads(response_data)
		requires_search = response_dict.get("requires_search", False)
		# print("check_call:\n", requires_search)
		return requires_search

def askllm(prompt, session_id = 1) -> str:
	response = ollama.embeddings(
		prompt=prompt,
		model="mxbai-embed-large"
		)
	##Get vectors
	query = "SELECT title, doc, link FROM pages ORDER BY embedding <=> %s LIMIT 1"
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
	print(resultstr)
	return resultstr

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=JSONResponse)
async def chat(request: Data):
	print("History:\n", request)
	user = request.messages[-1].get("content", "")
	# print(user)
	call = check_call(user)
	if call:
		# Perform a Google search
		search_results = search(user, num_results=1)
		search_results_str = "\n".join(search_results)
		first_result_url = " "
		clean_text = " "
		# if search_results:
		# 	first_result_url = search_results_str.split("\n")[0]
		# 	clean_text = get_text(first_result_url)
		# print(search_results)
		# Get the RAG response
		rag = askllm(user)
		# print("RAG:\n", rag)
		# Concatenate the search results and RAG response
		concat = f"Using this data: {first_result_url}\n{clean_text}\n{rag} to respond to this user question: {user}."
		request.messages[-1]["content"] = concat
	reply = ollama_request(request)
	if call:
		if rag:
			link_match = re.search(r"Link: (.+)\n", rag)
			link_value = link_match.group(1)
			reply = f"{reply}\nGoogle search:\n{first_result_url}\nNotion page:\n{link_value}"
	return {"message": {"role": "assistant", "content": reply}}

def ollama_request(request: Data):
	response = requests.post(OLLAMA_API, json=request.dict())
	response_json = response.json()
	content = response_json.get("message", {}).get("content", "")
	if not content:
		raise ValueError("Invalid response structure: 'content' not found")
	return content

def get_text(first_result_url):
	response = requests.get(first_result_url)
	# print(response)
	soup = BeautifulSoup(response.content, 'html.parser')
	page_text = soup.get_text()
	# clean text from html tags, etc.
	cleaned_text = " ".join(page_text.split())
	# print(cleaned_text)
	return cleaned_text

if __name__ == "__main__":
	uvicorn.run("app:app", host="0.0.0.0", port=8081, reload=True)