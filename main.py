from fastapi import FastAPI
from routes import auth, posts, users, followings
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(followings.router)


@app.get("/")
async def root():
    return {"message": "API is running"}
