from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return{"message":"Hellow from Docker Episode 4 "}