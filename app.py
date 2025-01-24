from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import requests
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


OLLAMA_API = "http://localhost:11434/api/chat"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_class=JSONResponse)
def chat(request: Data):
	print(request)
	reply = ollama_request(request)
	return {"message": {"role": "assistant", "content": reply}}

def ollama_request(request: Data):
	response = requests.post(OLLAMA_API, json=request.dict())
	response_json = response.json()
	content = response_json.get("message", {}).get("content", "")
	if not content:
		raise ValueError("Invalid response structure: 'content' not found")
	return content