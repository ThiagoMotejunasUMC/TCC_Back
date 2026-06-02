import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.crud.crud_movimentacao import (
    registrar_movimentacao, listar_movimentacoes,
    atualizar_movimentacao, deletar_movimentacao
)
from app.schemas.movimentacao_schema import MovimentacaoCreate


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    return db


def item_disponivel():
    item = MagicMock()
    item.id = 1
    item.ativo = True
    item.status = "disponivel"
    item.numero_serie = "SN001"
    item.produto_id = 1
    return item


class TestRegistrarMovimentacao:
    def test_saida_item_disponivel(self):
        db = mock_db()
        item = item_disponivel()
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="saida", motivo="Venda")
        with patch("app.crud.crud_movimentacao.registrar_log"), \
             patch("app.crud.crud_movimentacao.verificar_e_notificar_estoque"):
            registrar_movimentacao(db, data, usuario_id=1)
        assert item.status == "vendido"
        db.commit.assert_called()

    def test_saida_motivo_descarte_muda_para_danificado(self):
        db = mock_db()
        item = item_disponivel()
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="saida", motivo="Descarte")
        with patch("app.crud.crud_movimentacao.registrar_log"), \
             patch("app.crud.crud_movimentacao.verificar_e_notificar_estoque"):
            registrar_movimentacao(db, data, usuario_id=1)
        assert item.status == "danificado"

    def test_saida_motivo_manutencao_muda_para_em_manutencao(self):
        db = mock_db()
        item = item_disponivel()
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="saida", motivo="manutencao")
        with patch("app.crud.crud_movimentacao.registrar_log"), \
             patch("app.crud.crud_movimentacao.verificar_e_notificar_estoque"):
            registrar_movimentacao(db, data, usuario_id=1)
        assert item.status == "em_manutencao"

    def test_entrada_muda_status_para_disponivel(self):
        db = mock_db()
        item = MagicMock(id=1, ativo=True, status="em_manutencao", numero_serie="SN001", produto_id=1)
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="entrada", motivo="Devolução")
        with patch("app.crud.crud_movimentacao.registrar_log"), \
             patch("app.crud.crud_movimentacao.verificar_e_notificar_estoque"):
            registrar_movimentacao(db, data, usuario_id=1)
        assert item.status == "disponivel"

    def test_erro_item_nao_encontrado(self):
        db = mock_db()
        data = MovimentacaoCreate(item_id=999, tipo="saida", motivo="Venda")
        with pytest.raises(HTTPException) as exc:
            registrar_movimentacao(db, data, usuario_id=1)
        assert exc.value.status_code == 404

    def test_erro_item_inativo(self):
        db = mock_db()
        item = MagicMock(id=1, ativo=False, status="disponivel")
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="saida", motivo="Venda")
        with pytest.raises(HTTPException) as exc:
            registrar_movimentacao(db, data, usuario_id=1)
        assert exc.value.status_code == 400

    def test_erro_saida_item_nao_disponivel(self):
        db = mock_db()
        item = MagicMock(id=1, ativo=True, status="vendido", numero_serie="SN001")
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="saida", motivo="Venda")
        with pytest.raises(HTTPException) as exc:
            registrar_movimentacao(db, data, usuario_id=1)
        assert exc.value.status_code == 400
        assert "disponível" in exc.value.detail.lower()

    def test_erro_tipo_invalido(self):
        db = mock_db()
        item = item_disponivel()
        db.query.return_value.filter.return_value.first.return_value = item
        data = MovimentacaoCreate(item_id=1, tipo="invalido", motivo="Venda")
        with pytest.raises(HTTPException) as exc:
            registrar_movimentacao(db, data, usuario_id=1)
        assert exc.value.status_code == 400


class TestListarMovimentacoes:
    def test_lista_todas(self):
        db = MagicMock()
        db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_movimentacoes(db)
        assert isinstance(resultado, list)

    def test_filtra_por_tipo_entrada(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_movimentacoes(db, tipo="entrada")
        assert isinstance(resultado, list)

    def test_filtra_por_tipo_saida(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_movimentacoes(db, tipo="saida")
        assert isinstance(resultado, list)

    def test_filtra_por_item_id(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        resultado = listar_movimentacoes(db, item_id=1)
        assert isinstance(resultado, list)

class TestAtualizarMovimentacao:
    def test_atualiza_observacao(self):
        db = mock_db()
        mov_mock = MagicMock(id=1, observacao="antiga")
        db.query.return_value.filter.return_value.first.return_value = mov_mock
        with patch("app.crud.crud_movimentacao.registrar_log"):
            atualizar_movimentacao(db, 1, "nova observação", usuario_id=1)
        assert mov_mock.observacao == "nova observação"

    def test_erro_nao_encontrada(self):
        db = mock_db()
        with pytest.raises(HTTPException) as exc:
            atualizar_movimentacao(db, 999, "obs", usuario_id=1)
        assert exc.value.status_code == 404


class TestDeletarMovimentacao:
    def test_deleta_com_sucesso(self):
        db = mock_db()
        mov_mock = MagicMock(id=1, tipo="saida", motivo="Venda", item_id=1)
        item_mock = MagicMock(numero_serie="SN001")
        db.query.return_value.filter.return_value.first.side_effect = [mov_mock, item_mock]
        with patch("app.crud.crud_movimentacao.registrar_log"):
            deletar_movimentacao(db, 1, usuario_id=1)
        db.delete.assert_called_once_with(mov_mock)

    def test_erro_nao_encontrada(self):
        db = mock_db()
        with pytest.raises(HTTPException) as exc:
            deletar_movimentacao(db, 999, usuario_id=1)
        assert exc.value.status_code == 404