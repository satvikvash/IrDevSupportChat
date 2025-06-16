# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import json

app = FastAPI()

# Enable CORS so frontend can access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The stopwords variable is already available, so no need to import or download again.
def preprocess_text(text):
    # Lowercase
    text = text.lower()
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Tokenize into words
    words = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    
    # Join words back into a string
    preprocessed_text = ' '.join(words)
    
    return preprocessed_text

def load_index(index_path):
        return faiss.read_index(index_path)

# Load metadata function
def load_metadata(metadata_path):
    with open(metadata_path, 'rb') as f:
        return pickle.load(f)
    
GOOGLE_API_KEY = ""  # ← Replace with your key
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini model (free tier)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_answer(index_path, metadata_path, query, conversation_history):
    with open("emails_grouped.json", "r", encoding="utf-8") as file:
        thread_response = json.load(file)

    # Extract email contents and metadata
    email_contents = []
    metadata_list = []

    for subject, emails in thread_response.items():
        for email in emails:
            body = email.get("body", "")
            received = email.get("received_datetime", "")
            # Combine subject and body for embedding
            email_contents.append(f"Subject: {subject}\n{body}")
            metadata_list.append({
                "subject": subject,
                "received_datetime": received
            })
    # Reload index and metadata
    faiss_index = load_index(index_path)
    metadata_list = load_metadata(metadata_path)
    print("Index and metadata reloaded successfully.")

    query_embedding = model.encode([preprocess_text(query)], convert_to_numpy=True)

    # Perform FAISS search
    k = 3
    distances, indices = faiss_index.search(query_embedding, k)

    # Retrieve top emails and metadata as context
    threshold = 1.0
    # Retrieve top emails and metadata as context
    context_pieces = []
    for dist, idx in zip(distances[0], indices[0]):
        if dist < threshold:
            meta = metadata_list[idx]
            email_text = email_contents[idx]
            context_pieces.append(
                f"Received: {meta['received_datetime']}\n"
                f"Email:\n{email_text}")

    context = "\n\n---\n\n".join(context_pieces)

    history_str = ""
    if conversation_history:
        for q, a in conversation_history:
            history_str += f"User: {q}\nAssistant: {a}\n"
    # Prepare prompt for Gemini

    if context.strip():
        prompt = f"""You are a support assistant. Based on the relevant emails found below, provide:
        A brief description of the issue
        1. How to resolve this issue 
        2. When this happened before  
        3. Who was involved

        Relevant emails: {context}s
        History: {history_str}
        Question: {query}"""
    else:
        prompt = f"""You are a support assistant. No relevant past emails were found for this query.

        History: {history_str}
        Question: {query}

        Please help the user or ask clarifying questions to better understand their issue."""

    response = gemini_model.generate_content(prompt)
    print("\n🔍 Answer:")
    print(response.text)
    return response.text

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime

index_path = "email_faiss.index"
metadata_path = "email_metadata.pkl"
@app.post("/api/testMessage", response_model=ChatResponse)
async def test_message(req: ChatRequest):
    res = generate_answer(index_path,metadata_path,req.message,[])
    return ChatResponse(
        message=res,
        timestamp=datetime.now()
    )
