import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.crud.crud_fornecedor import (
    criar_fornecedor, listar_fornecedores,
    obter_fornecedor, atualizar_fornecedor, deletar_fornecedor
)
from app.schemas.fornecedor_schema import FornecedorCreate, FornecedorUpdate


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    return db


class TestCriarFornecedor:
    def test_cria_com_sucesso(self):
        db = mock_db()
        data = FornecedorCreate(nome="TechDistrib")
        with patch("app.crud.crud_fornecedor.registrar_log"):
            criar_fornecedor(db, data, usuario_id=1)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_cria_sem_usuario_id_nao_loga(self):
        db = mock_db()
        data = FornecedorCreate(nome="TechDistrib")
        with patch("app.crud.crud_fornecedor.registrar_log") as mock_log:
            criar_fornecedor(db, data)
        mock_log.assert_not_called()


class TestListarFornecedores:
    def test_lista_todos(self):
        db = mock_db()
        resultado = listar_fornecedores(db)
        assert isinstance(resultado, list)

    def test_filtra_por_busca(self):
        db = mock_db()
        db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_fornecedores(db, busca="Tech")
        assert isinstance(resultado, list)

    def test_retorna_lista_vazia(self):
        db = mock_db()
        resultado = listar_fornecedores(db)
        assert resultado == []


class TestObterFornecedor:
    def test_retorna_fornecedor_existente(self):
        db = mock_db()
        fornecedor_mock = MagicMock(id=1, nome="TechDistrib")
        db.query.return_value.filter.return_value.first.return_value = fornecedor_mock
        resultado = obter_fornecedor(db, 1)
        assert resultado.nome == "TechDistrib"

    def test_erro_nao_encontrado(self):
        db = mock_db()
        with pytest.raises(HTTPException) as exc:
            obter_fornecedor(db, 999)
        assert exc.value.status_code == 404


class TestAtualizarFornecedor:
    def test_atualiza_email(self):
        db = mock_db()
        fornecedor_mock = MagicMock(id=1, email="old@email.com")
        db.query.return_value.filter.return_value.first.return_value = fornecedor_mock
        data = FornecedorUpdate(email="new@email.com")
        with patch("app.crud.crud_fornecedor.registrar_log"):
            atualizar_fornecedor(db, 1, data, usuario_id=1)
        assert fornecedor_mock.email == "new@email.com"

    def test_atualiza_sem_usuario_id_nao_loga(self):
        db = mock_db()
        fornecedor_mock = MagicMock(id=1, nome="Tech")
        db.query.return_value.filter.return_value.first.return_value = fornecedor_mock
        data = FornecedorUpdate(nome="TechDistrib Pro")
        with patch("app.crud.crud_fornecedor.registrar_log") as mock_log:
            atualizar_fornecedor(db, 1, data)
        mock_log.assert_not_called()


class TestDeletarFornecedor:
    def test_desativa_fornecedor(self):
        db = mock_db()
        fornecedor_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = fornecedor_mock
        with patch("app.crud.crud_fornecedor.registrar_log"):
            deletar_fornecedor(db, 1, usuario_id=1)
        assert fornecedor_mock.ativo is False

    def test_deleta_sem_usuario_id_nao_loga(self):
        db = mock_db()
        fornecedor_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = fornecedor_mock
        with patch("app.crud.crud_fornecedor.registrar_log") as mock_log:
            deletar_fornecedor(db, 1)
        mock_log.assert_not_called()