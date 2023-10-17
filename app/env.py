from dotenv import load_dotenv
import os

def env(path: str):
    load_dotenv(path)
    env_dict = {}
    for key, value in os.environ.items():
        env_dict[key] = value
    return env_dict

env_vars = env(".env")
