from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import (
    usuario_model, produto_model, item_model,
    fornecedor_model, movimentacao_model, audit_model,
    categoria_model, password_reset_model,
    espaco_model, notificacao_model
)
from app.routers import (
    auth_router, usuario_router, categoria_router,
    produto_router, item_router, fornecedor_router,
    movimentacao_router, viacep_router,
    espaco_router, notificacao_router
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SGE — Sistema de Gerenciamento de Estoque")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(usuario_router.router)
app.include_router(categoria_router.router)
app.include_router(produto_router.router)
app.include_router(item_router.router)
app.include_router(fornecedor_router.router)
app.include_router(movimentacao_router.router)
app.include_router(viacep_router.router)
app.include_router(espaco_router.router)
app.include_router(notificacao_router.router)