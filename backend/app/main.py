from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.handlers import user, news, comment, auth

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(news.router)
app.include_router(comment.router)
app.include_router(auth.router)
