import asyncio
from app.core.database import init_db
from app.main import app

async def startup():
    await init_db()
    print("✅ Database initialized")

if __name__ == "__main__":
    import uvicorn
    asyncio.run(startup())
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
