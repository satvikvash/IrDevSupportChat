import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import json

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
    
GOOGLE_API_KEY = "AIzaSyA2yYyCH2ksVoCSQw3V3q65APjDmgSeZdg"  # ← Replace with your key
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
    context_pieces = []
    for idx in indices[0]:
        meta = metadata_list[idx]
        email_text = email_contents[idx]
        context_pieces.append(
            f"From: {meta['from_name']} <{meta['from_email']}>\n"
            f"Received: {meta['received_datetime']}\n"
            f"Email:\n{email_text}"
        )

    context = "\n\n---\n\n".join(context_pieces)

    history_str = ""
    if conversation_history:
        for q, a in conversation_history:
            history_str += f"User: {q}\nAssistant: {a}\n"
    # Prepare prompt for Gemini

    prompt = f"""You are an intelligent email assistant. Here is the conversation so far:
    {history_str}

    Emails:
    {context}

    Question: {query}

    Based on the emails above and the conversation history, please provide the following information:
    1. Possible Resolution: How to resolve the issue.
    2. Similar Issue Occurred: When the issue last occurred.
    3. Person Involved: Who was involved in this issue.

    Please give a concise and clear answer.
    """

    response = gemini_model.generate_content(prompt)
    print("\n🔍 Answer:")
    print(response.text)
    return response.text