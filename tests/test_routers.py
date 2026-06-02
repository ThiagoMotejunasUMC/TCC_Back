import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


class TestRotasPublicas:
    def test_login_sem_credenciais_retorna_422(self):
        response = client.post("/auth/login", json={})
        assert response.status_code == 422

    def test_login_credenciais_invalidas_retorna_401(self):
        with patch("app.routers.auth_router.obter_usuario_por_email", return_value=None):
            response = client.post("/auth/login", json={"email": "x@x.com", "password": "Senha@123"})
        assert response.status_code == 401

    def test_esqueci_senha_retorna_200_sempre(self):
        with patch("app.routers.auth_router.obter_usuario_por_email", return_value=None):
            response = client.post("/auth/esqueci-senha", json={"email": "naoexiste@sge.com"})
        assert response.status_code == 200


class TestRotasProtegidas:
    def test_listar_produtos_sem_token_retorna_401(self):
        response = client.get("/produtos/")
        assert response.status_code == 401

    def test_listar_itens_sem_token_retorna_401(self):
        response = client.get("/itens/")
        assert response.status_code == 401

    def test_listar_categorias_sem_token_retorna_401(self):
        response = client.get("/categorias/")
        assert response.status_code == 401

    def test_listar_fornecedores_sem_token_retorna_401(self):
        response = client.get("/fornecedores/")
        assert response.status_code == 401

    def test_listar_movimentacoes_sem_token_retorna_401(self):
        response = client.get("/movimentacoes/")
        assert response.status_code == 401

    def test_listar_espacos_sem_token_retorna_401(self):
        response = client.get("/espacos/")
        assert response.status_code == 401

    def test_listar_usuarios_sem_token_retorna_401(self):
        response = client.get("/usuarios/")
        assert response.status_code == 401

    def test_criar_usuario_sem_token_retorna_401(self):
        response = client.post("/usuarios/", json={})
        assert response.status_code == 401


class TestViacep:
    def test_cep_invalido_retorna_400(self):
        response = client.get("/viacep/123")
        assert response.status_code == 400

    def test_cep_nao_numerico_retorna_400(self):
        response = client.get("/viacep/abcdefgh")
        assert response.status_code == 400

    def test_cep_valido_consulta_api(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cep": "01310-100",
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP"
        }
        with patch("httpx.AsyncClient.get", return_value=mock_response):
            response = client.get("/viacep/01310100")
        assert response.status_code == 200