import os
from pathlib import Path

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///votes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = Path('./my_secret_key.txt').read_text().strip()