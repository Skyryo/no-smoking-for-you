from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routers import smoking_habits, questionnaire, diagnosis, result

app = FastAPI(
    title="No Smoking ADK API",
    description="禁煙支援アプリのバックエンドAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なドメインを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを追加（依存関係のないもののみ）
app.include_router(smoking_habits.router, prefix="/api/v1", tags=["smoking-habits"])
app.include_router(questionnaire.router, prefix="/api/v1", tags=["questionnaire"])
app.include_router(diagnosis.router, prefix="/api/v1", tags=["diagnosis"])
app.include_router(result.router, prefix="/api/v1", tags=["result"])

@app.get("/")
async def root():
    return {"message": "No Smoking ADK API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
