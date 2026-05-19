from fastapi import FastAPI
<<<<<<< HEAD
from routes import auth, posts, users
from dotenv import load_dotenv

load_dotenv()
=======
from routes import auth, posts, users, followings
>>>>>>> 8b9766d (remove sensitive files)

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)
<<<<<<< HEAD
=======
app.include_router(followings.router)

>>>>>>> 8b9766d (remove sensitive files)

@app.get("/")
async def root():
    return {"message": "API is running"}
