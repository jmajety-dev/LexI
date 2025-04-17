import os
import openai
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# Set OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Azure AI Search Details
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")

#  FastAPI App Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to Retrieve Documents + References from Azure AI Search
def search_documents(query):
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}/docs/search?api-version=2023-07-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }
    payload = {
        "search": query,
        "top": 5,  # Fetch top 5 relevant documents
        "select": "content,title",  # Retrieve content + metadata
        
        
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        results = response.json().get("value", [])
        documents = [{"content": doc["content"], "source": doc.get("source", "Unknown"), "title": doc.get("title", "No Title")} for doc in results]
        return documents
    else:
        print(f"Azure Search Error: {response.text}")
        return []

# Function to Generate AI Response + Reference Documents
def generate_response(question, retrieved_docs):
    context = "\n\n".join([doc["content"] for doc in retrieved_docs])
    references = [{"title": doc["title"], "source": doc["source"]} for doc in retrieved_docs]

    messages = [
        {"role": "system", "content": "You are an AI assistant specializing in US immigration law."},
        {"role": "user", "content": f"Using the following legal references:\n\n{context}\n\nAnswer this query: {question}"}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=messages
        )
        return response["choices"][0]["message"]["content"], references
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Sorry, an error occurred while generating the response.", []

# API Endpoint: Query AI Assistant with References
@app.get("/query") # Define the API endpoint
def query_lexi(question: str):
    try:
        retrieved_docs = search_documents(question)  # Fetch from Azure AI Search
        
        # Extracting only the text content for AI model
        doc_context = "\n".join([doc["content"] for doc in retrieved_docs])

        # Call OpenAI API with the retrieved context
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant specializing in immigration law."},
                {"role": "user", "content": f"Answer based on this context:\n\n{doc_context}\n\nQuestion: {question}"}
            ]
        )

        answer = response["choices"][0]["message"]["content"]

        # Return the response including the sources
        return {
            "answer": answer,
            "references": [{"title": doc["title"]} for doc in retrieved_docs]
        }

    except Exception as e:
        return {"answer": f"Error processing request: {str(e)}", "references": []}


