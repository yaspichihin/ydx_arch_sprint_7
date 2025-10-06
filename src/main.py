import uvicorn
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from get_index import get_db
from llm import llm_query

app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def query(payload: QueryRequest, k=20, db=Depends(get_db)):
    similarity = db.similarity_search(payload.query, k=k)
    response = llm_query(payload.query, similarity)
    return {"response": response}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
