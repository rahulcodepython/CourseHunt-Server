from dotenv import load_dotenv
import os

load_dotenv()

os.getenv("ENVIRONMENT", "local")

if os.getenv("ENVIRONMENT") == "production":
    from .production import *
else:
    from .local import *
