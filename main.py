from fastapi import FastAPI
from app.database import init_database
from app.routers import sales, stock, tags, chat

app = FastAPI(on_startup=[init_database])

app.include_router(sales.router)
app.include_router(stock.router)
app.include_router(tags.router)
app.include_router(chat.router)

@app.get("/")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    