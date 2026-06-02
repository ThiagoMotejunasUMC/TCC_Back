import pytest
from unittest.mock import MagicMock
from app.crud.crud_notificacao import (
    listar_notificacoes, contar_nao_lidas,
    marcar_como_lida, marcar_todas_como_lidas,
    limpar_lidas
)


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.count.return_value = 0
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.filter.return_value.update.return_value = None
    db.query.return_value.filter.return_value.filter.return_value.delete.return_value = None
    return db


class TestListarNotificacoes:
    def test_lista_todas_do_usuario(self):
        db = mock_db()
        resultado = listar_notificacoes(db, usuario_id=1)
        assert isinstance(resultado, list)
        db.query.assert_called_once()

    def test_lista_apenas_nao_lidas(self):
        db = mock_db()
        notif_mock = MagicMock(id=1, lida=False, usuario_id=1)
        db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [notif_mock]
        resultado = listar_notificacoes(db, usuario_id=1, apenas_nao_lidas=True)
        assert isinstance(resultado, list)

    def test_retorna_lista_vazia_sem_notificacoes(self):
        db = mock_db()
        resultado = listar_notificacoes(db, usuario_id=999)
        assert resultado == []


class TestContarNaoLidas:
    def test_retorna_zero_sem_notificacoes(self):
        db = mock_db()
        resultado = contar_nao_lidas(db, usuario_id=1)
        assert resultado == 0

    def test_retorna_contagem_correta(self):
        db = mock_db()
        db.query.return_value.filter.return_value.count.return_value = 5
        resultado = contar_nao_lidas(db, usuario_id=1)
        assert resultado == 5


class TestMarcarComoLida:
    def test_marca_notificacao_existente(self):
        db = mock_db()
        notif_mock = MagicMock(id=1, lida=False, usuario_id=1)
        db.query.return_value.filter.return_value.first.return_value = notif_mock
        resultado = marcar_como_lida(db, notificacao_id=1, usuario_id=1)
        assert resultado is True
        assert notif_mock.lida is True
        db.commit.assert_called_once()

    def test_retorna_false_notificacao_nao_encontrada(self):
        db = mock_db()
        resultado = marcar_como_lida(db, notificacao_id=999, usuario_id=1)
        assert resultado is False
        db.commit.assert_not_called()

    def test_nao_marca_notificacao_de_outro_usuario(self):
        db = mock_db()
        resultado = marcar_como_lida(db, notificacao_id=1, usuario_id=99)
        assert resultado is False


class TestMarcarTodasComoLidas:
    def test_atualiza_todas_nao_lidas(self):
        db = MagicMock()
        marcar_todas_como_lidas(db, usuario_id=1)
        db.commit.assert_called_once()

    def test_chama_update_com_lida_true(self):
        db = MagicMock()
        marcar_todas_como_lidas(db, usuario_id=1)
        update_call = db.query.return_value.filter.return_value.update
        update_call.assert_called_once_with({"lida": True})


class TestLimparLidas:
    def test_deleta_notificacoes_lidas(self):
        db = MagicMock()
        limpar_lidas(db, usuario_id=1)
        db.commit.assert_called_once()

    def test_chama_delete(self):
        db = MagicMock()
        limpar_lidas(db, usuario_id=1)
        delete_call = db.query.return_value.filter.return_value.delete
        delete_call.assert_called_once()