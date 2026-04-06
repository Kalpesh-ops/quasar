import os
import uvicorn
from fastapi.responses import HTMLResponse
from openenv.core.env_server import create_app
from src.env import QuasarEnv
from src.models import QuasarAction, QuasarObservation

app = create_app(QuasarEnv, QuasarAction, QuasarObservation)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Quasar OpenEnv</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                .container { text-align: center; max-width: 600px; padding: 2rem; background: #1e293b; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); border: 1px solid #334155; }
                h1 { color: #38bdf8; margin-bottom: 0.5rem; }
                p { color: #94a3b8; line-height: 1.6; }
                .badge { display: inline-block; padding: 0.25rem 0.75rem; background-color: #059669; color: #d1fae5; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; margin-top: 1rem; margin-bottom: 1rem; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌌 Quasar Defense Engine</h1>
                <div class="badge">Status: Online & Ready</div>
                <p>This is a headless OpenEnv Reinforcement Learning server. The simulation is actively waiting for agents.</p>
                <p>Available endpoints: <code>/step</code> | <code>/reset</code> | <code>/state</code></p>
                <p><em>Refer to the README in the repository files for connection and task documentation.</em></p>
            </div>
        </body>
    </html>
    """

def main():
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()