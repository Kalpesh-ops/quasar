import os
import uvicorn
from openenv.core.env_server import create_app
from src.env import QuasarEnv
from src.models import QuasarAction, QuasarObservation

app = create_app(QuasarEnv, QuasarAction, QuasarObservation)

def main():
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()