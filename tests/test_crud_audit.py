import pytest
from unittest.mock import MagicMock
from app.crud.crud_audit import registrar_log


class TestRegistrarLog:
    def test_cria_log_com_todos_campos(self):
        db = MagicMock()
        registrar_log(db, usuario_id=1, acao="CREATE", entidade="produto", entidade_id=5, detalhe="Produto criado: iPhone")
        db.add.assert_called_once()
        db.commit.assert_called_once()
        log_criado = db.add.call_args[0][0]
        assert log_criado.usuario_id == 1
        assert log_criado.acao == "CREATE"
        assert log_criado.entidade == "produto"
        assert log_criado.entidade_id == 5
        assert log_criado.detalhe == "Produto criado: iPhone"

    def test_cria_log_sem_entidade_id(self):
        db = MagicMock()
        registrar_log(db, usuario_id=2, acao="UPDATE", entidade="usuario")
        db.add.assert_called_once()
        log_criado = db.add.call_args[0][0]
        assert log_criado.entidade_id is None

    def test_cria_log_sem_detalhe(self):
        db = MagicMock()
        registrar_log(db, usuario_id=1, acao="DELETE", entidade="categoria", entidade_id=3)
        log_criado = db.add.call_args[0][0]
        assert log_criado.detalhe is None

    def test_retorna_log_criado(self):
        db = MagicMock()
        resultado = registrar_log(db, usuario_id=1, acao="CREATE", entidade="item", entidade_id=10)
        assert resultado is not None