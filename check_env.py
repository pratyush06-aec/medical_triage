import os
from dotenv import load_dotenv
load_dotenv()
print("ENV file bytes (first 8):")
with open(".env","rb") as f:
    print(list(f.read(8)))
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))
print("GOOGLE_GENAI_USE_VERTEXAI:", os.getenv("GOOGLE_GENAI_USE_VERTEXAI"))
