from fastapi import FastAPI
from pydantic import BaseModel

class Todos(BaseModel):
    id: int
    item: str