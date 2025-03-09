import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/query")
def query_lexi(question: str):
    try:
        # Simulating AI Response (Replace with OpenAI API or your ML model)
        response = {"answer": "(AI response placeholder)"}
        return response
    except Exception as e:
        return {"answer": f"Error processing request: {str(e)}"}

# Mission Statement from Murray Osorio PLLC
@app.get("/mission")
def mission_statement():
    return {
        "mission": "At Murray Osorio PLLC, we are committed to providing compassionate and high-quality legal services "
                   "to immigrants and their families. Our mission is to advocate for justice and protect the rights of "
                   "those seeking a better future."
    }
