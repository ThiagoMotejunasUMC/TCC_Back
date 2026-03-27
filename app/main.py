from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine

app = FastAPI(
    title="SGE - Sistema de Gerenciamento de Estoque",
    description="API para gerenciamento de estoque com controle de acesso por cargo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.models import (
    usuario_model,
    produto_model,
    variacao_model,
    fornecedor_model,
    movimentacao_model,
    audit_model
)

Base.metadata.create_all(bind=engine)

from app.routers import (
    auth_router,
    usuario_router,
    produto_router,
    variacao_router,
    fornecedor_router,
    movimentacao_router,
    viacep_router
)

app.include_router(auth_router.router)
app.include_router(usuario_router.router)
app.include_router(produto_router.router)
app.include_router(variacao_router.router)
app.include_router(fornecedor_router.router)
app.include_router(movimentacao_router.router)
app.include_router(viacep_router.router)

@app.get("/")
def home():
    return {"mensagem": "API SGE rodando"}