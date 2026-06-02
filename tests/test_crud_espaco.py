import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from app.crud.crud_espaco import (
    criar_espaco, listar_espacos, obter_espaco,
    atualizar_espaco, deletar_espaco,
    obter_ocupacao, verificar_capacidade_item
)
from app.schemas.espaco_schema import EspacoCreate, EspacoUpdate, EspacoOcupacao


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.all.return_value = []
    return db


class TestCriarEspaco:
    def test_cria_com_sucesso(self):
        db = mock_db()
        data = EspacoCreate(
            nome="Prateleira A1",
            largura_cm=100, altura_cm=50,
            profundidade_cm=40, peso_max_kg=200
        )
        with patch("app.crud.crud_espaco.registrar_log"):
            criar_espaco(db, data, usuario_id=1)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_cria_sem_usuario_id_nao_loga(self):
        db = mock_db()
        data = EspacoCreate(
            nome="Prateleira B1",
            largura_cm=50, altura_cm=50,
            profundidade_cm=50, peso_max_kg=100
        )
        with patch("app.crud.crud_espaco.registrar_log") as mock_log:
            criar_espaco(db, data)
        mock_log.assert_not_called()


class TestListarEspacos:
    def test_lista_apenas_ativos_por_padrao(self):
        db = mock_db()
        listar_espacos(db)
        db.query.assert_called_once()

    def test_lista_todos_quando_apenas_ativos_false(self):
        db = mock_db()
        listar_espacos(db, apenas_ativos=False)
        db.query.assert_called_once()

    def test_retorna_lista_vazia(self):
        db = mock_db()
        resultado = listar_espacos(db)
        assert resultado == []


class TestObterEspaco:
    def test_retorna_espaco_existente(self):
        db = mock_db()
        espaco_mock = MagicMock(id=1, nome="Prateleira A1")
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = obter_espaco(db, 1)
        assert resultado.nome == "Prateleira A1"

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        resultado = obter_espaco(db, 999)
        assert resultado is None


class TestAtualizarEspaco:
    def test_atualiza_com_sucesso(self):
        db = mock_db()
        espaco_mock = MagicMock(id=1, nome="Antigo")
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        data = EspacoUpdate(nome="Novo Nome")
        with patch("app.crud.crud_espaco.registrar_log"):
            resultado = atualizar_espaco(db, 1, data, usuario_id=1)
        assert espaco_mock.nome == "Novo Nome"
        db.commit.assert_called_once()

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        data = EspacoUpdate(nome="Novo")
        resultado = atualizar_espaco(db, 999, data)
        assert resultado is None


class TestDeletarEspaco:
    def test_desativa_espaco(self):
        db = mock_db()
        espaco_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        with patch("app.crud.crud_espaco.registrar_log"):
            deletar_espaco(db, 1, usuario_id=1)
        assert espaco_mock.ativo is False

    def test_retorna_none_se_nao_encontrado(self):
        db = mock_db()
        resultado = deletar_espaco(db, 999)
        assert resultado is None

    def test_deleta_sem_usuario_id_nao_loga(self):
        db = mock_db()
        espaco_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        with patch("app.crud.crud_espaco.registrar_log") as mock_log:
            deletar_espaco(db, 1)
        mock_log.assert_not_called()


class TestObterOcupacao:
    def test_retorna_ocupacao_correta(self):
        db = mock_db()
        espaco_mock = MagicMock()
        espaco_mock.id = 1
        espaco_mock.nome = "Prateleira A1"
        type(espaco_mock).volume_total_m3 = PropertyMock(return_value=1.0)
        type(espaco_mock).volume_ocupado_m3 = PropertyMock(return_value=0.5)
        type(espaco_mock).peso_max_kg = PropertyMock(return_value=500.0)
        type(espaco_mock).peso_ocupado_kg = PropertyMock(return_value=100.0)
        type(espaco_mock).percentual_volume = PropertyMock(return_value=50.0)
        type(espaco_mock).percentual_peso = PropertyMock(return_value=20.0)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = obter_ocupacao(db, 1)
        assert resultado is not None
        assert resultado.percentual_volume == 50.0
        assert resultado.percentual_peso == 20.0
        assert resultado.alerta_volume is False
        assert resultado.critico_volume is False

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        resultado = obter_ocupacao(db, 999)
        assert resultado is None

    def test_alerta_volume_quando_80_porcento(self):
        db = mock_db()
        espaco_mock = MagicMock()
        espaco_mock.id = 1
        espaco_mock.nome = "Prateleira B1"
        type(espaco_mock).volume_total_m3 = PropertyMock(return_value=1.0)
        type(espaco_mock).volume_ocupado_m3 = PropertyMock(return_value=0.8)
        type(espaco_mock).peso_max_kg = PropertyMock(return_value=500.0)
        type(espaco_mock).peso_ocupado_kg = PropertyMock(return_value=0.0)
        type(espaco_mock).percentual_volume = PropertyMock(return_value=80.0)
        type(espaco_mock).percentual_peso = PropertyMock(return_value=0.0)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = obter_ocupacao(db, 1)
        assert resultado.alerta_volume is True
        assert resultado.critico_volume is False

    def test_critico_volume_quando_100_porcento(self):
        db = mock_db()
        espaco_mock = MagicMock()
        espaco_mock.id = 1
        espaco_mock.nome = "Prateleira C1"
        type(espaco_mock).volume_total_m3 = PropertyMock(return_value=1.0)
        type(espaco_mock).volume_ocupado_m3 = PropertyMock(return_value=1.0)
        type(espaco_mock).peso_max_kg = PropertyMock(return_value=500.0)
        type(espaco_mock).peso_ocupado_kg = PropertyMock(return_value=0.0)
        type(espaco_mock).percentual_volume = PropertyMock(return_value=100.0)
        type(espaco_mock).percentual_peso = PropertyMock(return_value=0.0)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = obter_ocupacao(db, 1)
        assert resultado.critico_volume is True


class TestVerificarCapacidadeItem:
    def test_espaco_nao_encontrado(self):
        db = mock_db()
        resultado = verificar_capacidade_item(db, 999, 0.001, 1.0)
        assert resultado["valido"] is False
        assert "não encontrado" in resultado["erro"]

    def test_volume_disponivel_suficiente(self):
        db = mock_db()
        espaco_mock = MagicMock()
        type(espaco_mock).volume_total_m3 = PropertyMock(return_value=1.0)
        type(espaco_mock).volume_ocupado_m3 = PropertyMock(return_value=0.5)
        type(espaco_mock).peso_max_kg = PropertyMock(return_value=500.0)
        type(espaco_mock).peso_ocupado_kg = PropertyMock(return_value=100.0)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = verificar_capacidade_item(db, 1, 0.1, 1.0)
        assert resultado["valido"] is True

    def test_volume_insuficiente(self):
        db = mock_db()
        espaco_mock = MagicMock()
        type(espaco_mock).volume_total_m3 = PropertyMock(return_value=1.0)
        type(espaco_mock).volume_ocupado_m3 = PropertyMock(return_value=0.95)
        type(espaco_mock).peso_max_kg = PropertyMock(return_value=500.0)
        type(espaco_mock).peso_ocupado_kg = PropertyMock(return_value=100.0)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = verificar_capacidade_item(db, 1, 0.1, 1.0)
        assert resultado["valido"] is False
        assert "Volume" in resultado["erro"]

    def test_peso_excedido(self):
        db = mock_db()
        espaco_mock = MagicMock()
        type(espaco_mock).volume_total_m3 = PropertyMock(return_value=10.0)
        type(espaco_mock).volume_ocupado_m3 = PropertyMock(return_value=0.1)
        type(espaco_mock).peso_max_kg = PropertyMock(return_value=100.0)
        type(espaco_mock).peso_ocupado_kg = PropertyMock(return_value=99.0)
        db.query.return_value.filter.return_value.first.return_value = espaco_mock
        resultado = verificar_capacidade_item(db, 1, 0.001, 5.0)
        assert resultado["valido"] is False
        assert "Peso" in resultado["erro"]