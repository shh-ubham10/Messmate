import os
class Config:
    AUTH_TOKEN = os.getenv('AUTH_TOKEN')
    DATABASE = os.getenv('DATABASE')
