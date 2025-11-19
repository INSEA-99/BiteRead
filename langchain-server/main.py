from fastapi import FastAPI
from app.endpoints import feedback

app = FastAPI()

app.include_router(feedback.router)

@app.get("/")
def root():
    return {"message": "BiteRead LangChain server running!"}
