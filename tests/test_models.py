import pytest
from unittest.mock import MagicMock, PropertyMock
from app.models.item_model import Item
from app.models.espaco_model import Espaco


class TestItemVolumeM3:
    def test_volume_calculado_corretamente(self):
        item = Item()
        item.largura_cm = 10.0
        item.altura_cm = 20.0
        item.profundidade_cm = 5.0
        assert item.volume_m3 == pytest.approx(0.001, rel=1e-3)

    def test_volume_com_dimensoes_reais_iphone(self):
        item = Item()
        item.largura_cm = 7.69
        item.altura_cm = 15.99
        item.profundidade_cm = 0.83
        volume = (7.69 * 15.99 * 0.83) / 1_000_000
        assert item.volume_m3 == pytest.approx(volume, rel=1e-3)

    def test_volume_zero_quando_largura_none(self):
        item = Item()
        item.largura_cm = None
        item.altura_cm = 10.0
        item.profundidade_cm = 5.0
        assert item.volume_m3 == 0.0

    def test_volume_zero_quando_altura_none(self):
        item = Item()
        item.largura_cm = 10.0
        item.altura_cm = None
        item.profundidade_cm = 5.0
        assert item.volume_m3 == 0.0

    def test_volume_zero_quando_profundidade_none(self):
        item = Item()
        item.largura_cm = 10.0
        item.altura_cm = 10.0
        item.profundidade_cm = None
        assert item.volume_m3 == 0.0

    def test_volume_zero_quando_todas_dimensoes_none(self):
        item = Item()
        item.largura_cm = None
        item.altura_cm = None
        item.profundidade_cm = None
        assert item.volume_m3 == 0.0

    def test_volume_m3_formula_correta(self):
        item = Item()
        item.largura_cm = 100.0
        item.altura_cm = 100.0
        item.profundidade_cm = 100.0
        assert item.volume_m3 == pytest.approx(1.0, rel=1e-6)


class TestEspacoVolumeTotal:
    def test_volume_total_calculado_corretamente(self):
        espaco = Espaco()
        espaco.largura_cm = 200.0
        espaco.altura_cm = 180.0
        espaco.profundidade_cm = 60.0
        assert espaco.volume_total_m3 == pytest.approx(2.16, rel=1e-3)

    def test_volume_total_cubo_100cm(self):
        espaco = Espaco()
        espaco.largura_cm = 100.0
        espaco.altura_cm = 100.0
        espaco.profundidade_cm = 100.0
        assert espaco.volume_total_m3 == pytest.approx(1.0, rel=1e-6)

    def test_volume_total_dimensoes_pequenas(self):
        espaco = Espaco()
        espaco.largura_cm = 30.0
        espaco.altura_cm = 20.0
        espaco.profundidade_cm = 10.0
        assert espaco.volume_total_m3 == pytest.approx(0.006, rel=1e-3)


class TestEspacoOcupacao:
    def _criar_espaco_com_itens(self, largura, altura, profundidade, peso_max, itens):
        espaco = Espaco()
        espaco.largura_cm = largura
        espaco.altura_cm = altura
        espaco.profundidade_cm = profundidade
        espaco.peso_max_kg = peso_max
        espaco.itens = itens
        return espaco

    def _criar_item_mock(self, largura, altura, profundidade, peso, ativo=True):
        item = MagicMock()
        item.ativo = ativo
        item.largura_cm = largura
        item.altura_cm = altura
        item.profundidade_cm = profundidade
        item.peso_kg = peso
        volume = (largura * altura * profundidade) / 1_000_000 if all([largura, altura, profundidade]) else 0.0
        type(item).volume_m3 = PropertyMock(return_value=volume)
        return item

    def test_volume_ocupado_soma_itens_ativos(self):
        item1 = self._criar_item_mock(10, 10, 10, 1.0)
        item2 = self._criar_item_mock(10, 10, 10, 1.0)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item1, item2])
        assert espaco.volume_ocupado_m3 == pytest.approx(0.002, rel=1e-3)

    def test_volume_ocupado_ignora_itens_inativos(self):
        item_ativo = self._criar_item_mock(10, 10, 10, 1.0, ativo=True)
        item_inativo = self._criar_item_mock(10, 10, 10, 1.0, ativo=False)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item_ativo, item_inativo])
        assert espaco.volume_ocupado_m3 == pytest.approx(0.001, rel=1e-3)

    def test_peso_ocupado_soma_itens_ativos(self):
        item1 = self._criar_item_mock(10, 10, 10, 2.5)
        item2 = self._criar_item_mock(10, 10, 10, 1.5)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item1, item2])
        assert espaco.peso_ocupado_kg == pytest.approx(4.0, rel=1e-3)

    def test_percentual_volume_50_porcento(self):
        item = self._criar_item_mock(100, 100, 50, 1.0)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item])
        assert espaco.percentual_volume == pytest.approx(50.0, rel=1e-1)

    def test_percentual_volume_acima_100_limitado_a_100(self):
        item1 = self._criar_item_mock(100, 100, 50, 1.0)
        item2 = self._criar_item_mock(100, 100, 50, 1.0)
        item3 = self._criar_item_mock(100, 100, 50, 1.0)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item1, item2, item3])
        assert espaco.percentual_volume == pytest.approx(100.0, rel=1e-1)

    def test_volume_ocupado_pode_ultrapassar_total(self):
        item1 = self._criar_item_mock(100, 100, 50, 1.0)
        item2 = self._criar_item_mock(100, 100, 50, 1.0)
        item3 = self._criar_item_mock(100, 100, 50, 1.0)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item1, item2, item3])
        assert espaco.volume_ocupado_m3 > espaco.volume_total_m3

    def test_percentual_peso_alerta_80(self):
        item = self._criar_item_mock(10, 10, 10, 400.0)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item])
        assert espaco.percentual_peso == pytest.approx(80.0, rel=1e-1)

    def test_percentual_peso_critico_100(self):
        item = self._criar_item_mock(10, 10, 10, 500.0)
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [item])
        assert espaco.percentual_peso == pytest.approx(100.0, rel=1e-1)

    def test_espaco_sem_itens_percentuais_zero(self):
        espaco = self._criar_espaco_com_itens(100, 100, 100, 500, [])
        assert espaco.volume_ocupado_m3 == 0.0
        assert espaco.peso_ocupado_kg == 0.0
        assert espaco.percentual_volume == 0.0
        assert espaco.percentual_peso == 0.0

    def test_percentual_volume_zero_quando_volume_total_zero(self):
        espaco = Espaco()
        espaco.largura_cm = 0.0
        espaco.altura_cm = 100.0
        espaco.profundidade_cm = 100.0
        espaco.peso_max_kg = 500.0
        espaco.itens = []
        assert espaco.percentual_volume == 0.0

    def test_percentual_peso_zero_quando_peso_max_zero(self):
        espaco = Espaco()
        espaco.largura_cm = 100.0
        espaco.altura_cm = 100.0
        espaco.profundidade_cm = 100.0
        espaco.peso_max_kg = 0.0
        espaco.itens = []
        assert espaco.percentual_peso == 0.0