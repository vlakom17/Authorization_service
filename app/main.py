from fastapi import FastAPI
import subprocess
from app.api.auth import auth_router
from app.api.users import user_router
from app.api.logs import logs_router

app = FastAPI(title="Auth Service")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(logs_router, prefix="/logs", tags=["logs"])

@app.on_event("startup")
def apply_migrations():
    
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при применении миграций: {e}")

@app.get("/")
def root():
    return {"message": "Auth Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80, reload=False)
