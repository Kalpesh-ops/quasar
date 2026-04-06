import os
import uvicorn
from openenv.server import create_app
from src.env import QuasarEnv

# Initialize the OpenEnv FastAPI wrapper with your specific environment
app = create_app(QuasarEnv)

def main():
    # Hugging Face Spaces strictly requires binding to port 7860
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()