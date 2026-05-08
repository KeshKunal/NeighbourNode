from fastapi import FastAPI
from app.api.routes import items, borrow, users

app = FastAPI(title="NeighbourNode API")

app.include_router(items.router)
app.include_router(borrow.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "NeighbourNode API is running"}
