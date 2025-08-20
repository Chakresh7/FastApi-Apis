from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/chakresh")
def add(a:int ,b:int) -> int:
    return a+b

class SubtractModel(BaseModel):
    a:int
    b:int

def subtract(a:int ,b:int) -> int:
    return a-b

@app.post('/subtract')
def subtract_number(model:SubtractModel):
    return subtract(model.a,model.b)

print(add(3,4))
