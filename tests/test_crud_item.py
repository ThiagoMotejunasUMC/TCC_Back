import pytest
from unittest.mock import MagicMock, patch
from app.crud.crud_item import (
    criar_item, listar_itens, obter_item,
    atualizar_item, deletar_item,
    listar_alertas_estoque, verificar_e_notificar_estoque
)
from app.schemas.item_schema import ItemCreate, ItemUpdate


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.count.return_value = 0
    db.query.return_value.filter.return_value.filter.return_value.count.return_value = 0
    db.query.return_value.filter.return_value.filter.return_value.filter.return_value.count.return_value = 0
    return db


class TestCriarItem:
    def test_cria_com_sucesso(self):
        db = mock_db()
        data = ItemCreate(
            produto_id=1, numero_serie="SN001",
            preco_custo=100.0, preco_venda=150.0
        )
        with patch("app.crud.crud_item.registrar_log"), \
             patch("app.crud.crud_item.verificar_e_notificar_estoque"):
            criar_item(db, data, usuario_id=1)
        db.add.assert_called_once()
        db.commit.assert_called()

    def test_chama_verificar_estoque_apos_criar(self):
        db = mock_db()
        data = ItemCreate(
            produto_id=5, numero_serie="SN002",
            preco_custo=100.0, preco_venda=150.0
        )
        with patch("app.crud.crud_item.registrar_log"), \
             patch("app.crud.crud_item.verificar_e_notificar_estoque") as mock_notif:
            criar_item(db, data, usuario_id=1)
        mock_notif.assert_called_once()

    def test_cria_sem_usuario_id_nao_loga(self):
        db = mock_db()
        data = ItemCreate(
            produto_id=1, numero_serie="SN003",
            preco_custo=100.0, preco_venda=150.0
        )
        with patch("app.crud.crud_item.registrar_log") as mock_log, \
             patch("app.crud.crud_item.verificar_e_notificar_estoque"):
            criar_item(db, data)
        mock_log.assert_not_called()


class TestListarItens:
    def test_lista_todos_ativos(self):
        db = mock_db()
        db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_itens(db)
        assert isinstance(resultado, list)

    def test_filtra_por_produto_id(self):
        db = mock_db()
        db.query.return_value.filter.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_itens(db, produto_id=1)
        assert isinstance(resultado, list)

    def test_filtra_por_status(self):
        db = mock_db()
        db.query.return_value.filter.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_itens(db, status="disponivel")
        assert isinstance(resultado, list)

    def test_filtra_por_espaco_id(self):
        db = mock_db()
        db.query.return_value.filter.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_itens(db, espaco_id=1)
        assert isinstance(resultado, list)


class TestObterItem:
    def test_retorna_item_existente(self):
        db = mock_db()
        item_mock = MagicMock(id=1, numero_serie="SN001")
        db.query.return_value.filter.return_value.first.return_value = item_mock
        resultado = obter_item(db, 1)
        assert resultado.numero_serie == "SN001"

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        resultado = obter_item(db, 999)
        assert resultado is None


class TestAtualizarItem:
    def test_atualiza_com_sucesso(self):
        db = mock_db()
        item_mock = MagicMock(id=1, cor="Preto", numero_serie="SN001")
        db.query.return_value.filter.return_value.first.return_value = item_mock
        data = ItemUpdate(cor="Branco")
        with patch("app.crud.crud_item.registrar_log"):
            resultado = atualizar_item(db, 1, data, usuario_id=1)
        assert item_mock.cor == "Branco"
        db.commit.assert_called_once()

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        data = ItemUpdate(cor="Branco")
        resultado = atualizar_item(db, 999, data)
        assert resultado is None

    def test_atualiza_sem_usuario_id_nao_loga(self):
        db = mock_db()
        item_mock = MagicMock(id=1, cor="Preto", numero_serie="SN001")
        db.query.return_value.filter.return_value.first.return_value = item_mock
        data = ItemUpdate(cor="Azul")
        with patch("app.crud.crud_item.registrar_log") as mock_log:
            atualizar_item(db, 1, data)
        mock_log.assert_not_called()


class TestDeletarItem:
    def test_desativa_item(self):
        db = mock_db()
        item_mock = MagicMock(id=1, ativo=True, numero_serie="SN001")
        db.query.return_value.filter.return_value.first.return_value = item_mock
        with patch("app.crud.crud_item.registrar_log"):
            deletar_item(db, 1, usuario_id=1)
        assert item_mock.ativo is False

    def test_retorna_none_se_nao_encontrado(self):
        db = mock_db()
        resultado = deletar_item(db, 999)
        assert resultado is None

    def test_deleta_sem_usuario_id_nao_loga(self):
        db = mock_db()
        item_mock = MagicMock(id=1, ativo=True, numero_serie="SN001")
        db.query.return_value.filter.return_value.first.return_value = item_mock
        with patch("app.crud.crud_item.registrar_log") as mock_log:
            deletar_item(db, 1)
        mock_log.assert_not_called()


class TestListarAlertasEstoque:
    def test_retorna_lista_vazia_sem_produtos(self):
        db = mock_db()
        db.query.return_value.filter.return_value.all.return_value = []
        resultado = listar_alertas_estoque(db)
        assert resultado == []

    def test_adiciona_alerta_quando_abaixo_minimo(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, nome="iPhone", estoque_minimo=5, ativo=True)
        db.query.return_value.filter.return_value.all.return_value = [produto_mock]
        db.query.return_value.filter.return_value.count.return_value = 2
        resultado = listar_alertas_estoque(db)
        assert len(resultado) == 1
        assert resultado[0].produto_nome == "iPhone"

    def test_nao_adiciona_alerta_quando_acima_minimo(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, nome="iPhone", estoque_minimo=5, ativo=True)
        db.query.return_value.filter.return_value.all.return_value = [produto_mock]
        db.query.return_value.filter.return_value.count.return_value = 10
        resultado = listar_alertas_estoque(db)
        assert len(resultado) == 0


class TestVerificarENotificarEstoque:
    def test_nao_notifica_estoque_acima_minimo(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, nome="iPhone", estoque_minimo=3)
        db.query.return_value.filter.return_value.first.return_value = produto_mock
        db.query.return_value.filter.return_value.count.return_value = 10
        with patch("app.crud.crud_item.enviar_email_alerta_estoque") as mock_email:
            verificar_e_notificar_estoque(db, 1)
        mock_email.assert_not_called()

    def test_notifica_quando_estoque_igual_minimo(self):
        produto_mock = MagicMock(id=1, nome="iPhone", estoque_minimo=3)
        usuario_mock = MagicMock(
            id=1, email="admin@sge.com",
            nome="Admin", ativo=True, cargo="admin"
        )

        mock_produto_query = MagicMock()
        mock_produto_query.filter.return_value.first.return_value = produto_mock

        mock_item_query = MagicMock()
        mock_item_query.filter.return_value.count.return_value = 3

        mock_usuario_query = MagicMock()
        mock_usuario_query.filter.return_value.all.return_value = [usuario_mock]

        mock_notif_query = MagicMock()
        mock_notif_query.filter.return_value.first.return_value = None

        from app.models.produto_model import Produto
        from app.models.item_model import Item
        from app.models.usuario_model import Usuario
        from app.models.notificacao_model import Notificacao

        def query_side_effect(model):
            if model is Produto:
                return mock_produto_query
            elif model is Item:
                return mock_item_query
            elif model is Usuario:
                return mock_usuario_query
            elif model is Notificacao:
                return mock_notif_query
            return MagicMock()

        db = MagicMock()
        db.query.side_effect = query_side_effect

        with patch("app.crud.crud_item.enviar_email_alerta_estoque") as mock_email:
            verificar_e_notificar_estoque(db, 1)

        mock_email.assert_called_once()

    def test_nao_notifica_se_produto_nao_encontrado(self):
        db = mock_db()
        with patch("app.crud.crud_item.enviar_email_alerta_estoque") as mock_email:
            verificar_e_notificar_estoque(db, 999)
        mock_email.assert_not_called()

    def test_nao_duplica_notificacao_existente(self):
        db = mock_db()
        produto_mock = MagicMock(id=1, nome="iPhone", estoque_minimo=3)
        usuario_mock = MagicMock(
            id=1, email="admin@sge.com",
            nome="Admin", ativo=True, cargo="admin"
        )
        notif_existente = MagicMock()
        db.query.return_value.filter.return_value.first.side_effect = [produto_mock, notif_existente]
        db.query.return_value.filter.return_value.count.return_value = 2
        db.query.return_value.filter.return_value.filter.return_value.all.return_value = [usuario_mock]
        with patch("app.crud.crud_item.enviar_email_alerta_estoque") as mock_email:
            verificar_e_notificar_estoque(db, 1)
        mock_email.assert_not_called()