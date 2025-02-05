import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///votes.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Read the secret key from a file 
with open(os.path.join(os.path.dirname(__file__), 'my_secret_key.txt'), 'r') as f:
    SECRET_KEY = f.read().strip()