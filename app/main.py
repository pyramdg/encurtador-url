import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routers import links, redirect

# Cria as tabelas do banco automaticamente na inicialização
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API de Encurtador de URLs com expiração, redirecionamento ultrarrápido e rastreamento de métricas."
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}

# Rota raiz que serve o Frontend interativo
STATIC_INDEX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")

@app.get("/", include_in_schema=False)
def serve_home():
    if os.path.exists(STATIC_INDEX):
        return FileResponse(STATIC_INDEX)
    return {"message": "Encurtador de URLs API. Acesse /docs para documentação Swagger."}

# Inclui rotas de links (criação e estatísticas)
app.include_router(links.router)

# Rota de redirecionamento por último (captura /{codigo})
app.include_router(redirect.router)
