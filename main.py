from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes import auth, posts, users, followings
from dotenv import load_dotenv
from routes import socket

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(followings.router)
app.include_router(socket.router)


@app.get("/")
async def frontend():
    return FileResponse("static/index.html")
