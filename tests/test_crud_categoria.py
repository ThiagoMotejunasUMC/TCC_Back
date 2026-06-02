import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.crud.crud_categoria import (
    criar_categoria, listar_categorias,
    obter_categoria, atualizar_categoria, deletar_categoria
)
from app.schemas.categoria_schema import CategoriaCreate, CategoriaUpdate


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    return db


class TestCriarCategoria:
    def test_cria_categoria_com_sucesso(self):
        db = mock_db()
        data = CategoriaCreate(nome="Smartphones", descricao="Celulares")
        with patch("app.crud.crud_categoria.registrar_log"):
            categoria = criar_categoria(db, data, usuario_id=1)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_erro_nome_duplicado(self):
        db = mock_db()
        db.query.return_value.filter.return_value.first.return_value = MagicMock()
        data = CategoriaCreate(nome="Smartphones")
        with pytest.raises(HTTPException) as exc:
            criar_categoria(db, data, usuario_id=1)
        assert exc.value.status_code == 400

    def test_cria_sem_usuario_id(self):
        db = mock_db()
        data = CategoriaCreate(nome="Notebooks")
        with patch("app.crud.crud_categoria.registrar_log") as mock_log:
            criar_categoria(db, data)
        mock_log.assert_not_called()


class TestListarCategorias:
    def test_lista_todas(self):
        db = mock_db()
        listar_categorias(db)
        db.query.assert_called_once()

    def test_filtra_apenas_ativas(self):
        db = mock_db()
        listar_categorias(db, apenas_ativas=True)
        db.query.assert_called_once()


class TestObterCategoria:
    def test_retorna_categoria_existente(self):
        db = mock_db()
        categoria_mock = MagicMock(id=1, nome="Smartphones")
        db.query.return_value.filter.return_value.first.return_value = categoria_mock
        resultado = obter_categoria(db, 1)
        assert resultado.id == 1

    def test_erro_categoria_nao_encontrada(self):
        db = mock_db()
        with pytest.raises(HTTPException) as exc:
            obter_categoria(db, 999)
        assert exc.value.status_code == 404


class TestAtualizarCategoria:
    def test_atualiza_com_sucesso(self):
        db = mock_db()
        categoria_mock = MagicMock(id=1, nome="Smartphones")
        db.query.return_value.filter.return_value.first.return_value = categoria_mock
        data = CategoriaUpdate(descricao="Nova descrição")
        with patch("app.crud.crud_categoria.registrar_log"):
            resultado = atualizar_categoria(db, 1, data, usuario_id=1)
        db.commit.assert_called_once()


class TestDeletarCategoria:
    def test_desativa_com_sucesso(self):
        db = mock_db()
        categoria_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = categoria_mock
        with patch("app.crud.crud_categoria.registrar_log"):
            resultado = deletar_categoria(db, 1, usuario_id=1)
        assert categoria_mock.ativo is False
        db.commit.assert_called_once()