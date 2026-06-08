from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import subprocess
import os

from database.connection import get_session
from database.models import Topic

app = FastAPI(title="Automate.sh Dashboard")

# Determine the absolute path to the templates directory
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Render the main dashboard."""
    with get_session() as session:
        # Fetch stats
        total_topics = session.query(Topic).count()
        published = session.query(Topic).filter(Topic.status == "PUBLISHED").count()
        queued = session.query(Topic).filter(Topic.status == "TODO").count()
        
        # Fetch recent topics
        recent_topics = session.query(Topic).order_by(Topic.created_at.desc()).limit(20).all()
        
        return templates.TemplateResponse(request, "index.html", {
            "total_topics": total_topics,
            "published": published,
            "queued": queued,
            "topics": recent_topics
        })

@app.get("/api/topics")
async def get_topics():
    """API endpoint to get topics as JSON."""
    with get_session() as session:
        topics = session.query(Topic).order_by(Topic.created_at.desc()).limit(50).all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "category": t.category.value,
                "status": t.status.value,
                "quality_score": t.quality_score,
                "created_at": t.created_at.isoformat() if t.created_at else None
            }
            for t in topics
        ]

def run_background_task(command: list[str]):
    """Run a CLI command in the background."""
    env = os.environ.copy()
    # Add project root to PYTHONPATH so cli.py can import local modules
    env["PYTHONPATH"] = str(BASE_DIR.parent)
    # Run the cli.py from the project root
    subprocess.Popen(command, cwd=str(BASE_DIR.parent), env=env)

@app.post("/api/trigger")
async def trigger_run(background_tasks: BackgroundTasks):
    """Trigger the auto-publish pipeline."""
    # Spawn the CLI command in the background so it doesn't block the API
    background_tasks.add_task(run_background_task, ["python", "cli.py", "auto-publish"])
    return {"message": "Auto-publish pipeline triggered!"}

@app.post("/api/discover")
async def trigger_discover(background_tasks: BackgroundTasks):
    """Trigger the trending topics discovery."""
    background_tasks.add_task(run_background_task, ["python", "cli.py", "trends"])
    return {"message": "Trend discovery triggered!"}
