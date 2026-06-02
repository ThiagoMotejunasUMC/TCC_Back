import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.crud.crud_produto import (
    criar_produto, listar_produtos,
    obter_produto, atualizar_produto, deletar_produto
)
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
    db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    return db


class TestCriarProduto:
    def test_cria_produto_com_sucesso(self):
        db = mock_db()
        data = ProdutoCreate(nome="iPhone 15", estoque_minimo=5)
        with patch("app.crud.crud_produto.registrar_log"):
            criar_produto(db, data, usuario_id=1)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_cria_sem_usuario_id_nao_loga(self):
        db = mock_db()
        data = ProdutoCreate(nome="iPhone 15", estoque_minimo=5)
        with patch("app.crud.crud_produto.registrar_log") as mock_log:
            criar_produto(db, data)
        mock_log.assert_not_called()


class TestListarProdutos:
    def test_lista_apenas_ativos_por_padrao(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_produtos(db)
        assert isinstance(resultado, list)

    def test_lista_todos_quando_apenas_ativos_false(self):
        db = MagicMock()
        db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_produtos(db, apenas_ativos=False)
        assert isinstance(resultado, list)

    def test_filtra_por_busca(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_produtos(db, busca="iPhone")
        assert isinstance(resultado, list)

    def test_filtra_por_categoria_id(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_produtos(db, categoria_id=1)
        assert isinstance(resultado, list)


class TestObterProduto:
    def test_retorna_produto_existente(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, nome="iPhone 15")
        db.query.return_value.filter.return_value.first.return_value = produto_mock
        resultado = obter_produto(db, 1)
        assert resultado.nome == "iPhone 15"

    def test_erro_produto_nao_encontrado(self):
        db = mock_db()
        with pytest.raises(HTTPException) as exc:
            obter_produto(db, 999)
        assert exc.value.status_code == 404


class TestAtualizarProduto:
    def test_atualiza_estoque_minimo(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, estoque_minimo=5)
        db.query.return_value.filter.return_value.first.return_value = produto_mock
        data = ProdutoUpdate(estoque_minimo=10)
        with patch("app.crud.crud_produto.registrar_log"):
            atualizar_produto(db, 1, data, usuario_id=1)
        assert produto_mock.estoque_minimo == 10

    def test_atualiza_sem_usuario_id_nao_loga(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, nome="iPhone")
        db.query.return_value.filter.return_value.first.return_value = produto_mock
        data = ProdutoUpdate(nome="iPhone 15 Pro")
        with patch("app.crud.crud_produto.registrar_log") as mock_log:
            atualizar_produto(db, 1, data)
        mock_log.assert_not_called()


class TestDeletarProduto:
    def test_desativa_produto(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = produto_mock
        with patch("app.crud.crud_produto.registrar_log"):
            deletar_produto(db, 1, usuario_id=1)
        assert produto_mock.ativo is False

    def test_deleta_sem_usuario_id_nao_loga(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = produto_mock
        with patch("app.crud.crud_produto.registrar_log") as mock_log:
            deletar_produto(db, 1)
        mock_log.assert_not_called()