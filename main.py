import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from db import get_db_session
from models import JobBoard, JobPost

app = FastAPI()

@app.get("/api/health")
async def health():
  try:
    with get_db_session() as session:
        session.execute(text("SELECT 1"))
        return {"database": "ok"}
  except Exception as e:
    print(e)
    return {"database": "down"}

@app.get("/api/job-boards")
async def api_job_boards():
    with get_db_session() as session:
       jobBoards = session.query(JobBoard).all()
       return jobBoards
    
@app.get("/api/job-boards/{job_board_id}/job-posts")
async def api_company_job_board(job_board_id):
  with get_db_session() as session:
     jobPosts = session.query(JobPost).filter(JobPost.job_board_id.__eq__(job_board_id)).all()
     return jobPosts

@app.get("/api/job-boards/{slug}")
async def api_company_job_board(slug):
  with get_db_session() as session:
     jobPosts = session.query(JobPost) \
        .join(JobPost.job_board) \
        .filter(JobBoard.slug.__eq__(slug)) \
        .all()
     return jobPosts
  
app.mount("/app", StaticFiles(directory="frontend/dist"))

@app.get("/")
async def root():
  indexFilePath = os.path.join("frontend", "dist", "index.html")
  return FileResponse(path=indexFilePath, media_type="text/html")

@app.get("/{full_path:path}")
async def catch_all_redirect(full_path: str):
   return RedirectResponse(url="/")