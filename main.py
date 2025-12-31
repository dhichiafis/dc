from fastapi import FastAPI
import uvicorn 


app=FastAPI()


@app.get('/')
async def home():
    return {'message':'the home page'}