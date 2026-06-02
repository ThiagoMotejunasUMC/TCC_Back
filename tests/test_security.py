import pytest
from datetime import timedelta
from unittest.mock import patch
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_token, validate_password_strength
)


class TestHashPassword:
    def test_gera_hash_diferente_da_senha_original(self):
        senha = "Senha@123"
        hashed = hash_password(senha)
        assert hashed != senha

    def test_gera_hashes_distintos_para_mesma_senha(self):
        senha = "Senha@123"
        hash1 = hash_password(senha)
        hash2 = hash_password(senha)
        assert hash1 != hash2

    def test_hash_nao_vazio(self):
        hashed = hash_password("Senha@123")
        assert len(hashed) > 0


class TestVerifyPassword:
    def test_senha_correta_retorna_true(self):
        senha = "Senha@123"
        hashed = hash_password(senha)
        assert verify_password(senha, hashed) is True

    def test_senha_incorreta_retorna_false(self):
        hashed = hash_password("Senha@123")
        assert verify_password("SenhaErrada@1", hashed) is False

    def test_senha_vazia_retorna_false(self):
        hashed = hash_password("Senha@123")
        assert verify_password("", hashed) is False


class TestCreateAccessToken:
    def test_cria_token_valido(self):
        payload = {"sub": "1", "cargo": "admin"}
        token = create_access_token(payload, expires_delta=timedelta(minutes=30))
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_payload_decodificavel(self):
        payload = {"sub": "42", "cargo": "operador"}
        token = create_access_token(payload, expires_delta=timedelta(minutes=30))
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded["sub"] == "42"
        assert decoded["cargo"] == "operador"

    def test_token_com_primeiro_acesso(self):
        payload = {"sub": "1", "cargo": "admin", "primeiro_acesso": True}
        token = create_access_token(payload, expires_delta=timedelta(minutes=30))
        decoded = verify_token(token)
        assert decoded["primeiro_acesso"] is True


class TestCreateRefreshToken:
    def test_cria_refresh_token_valido(self):
        payload = {"sub": "1"}
        token = create_refresh_token(payload)
        assert token is not None
        assert isinstance(token, str)

    def test_refresh_token_tem_type_refresh(self):
        payload = {"sub": "1"}
        token = create_refresh_token(payload)
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded.get("type") == "refresh"


class TestVerifyToken:
    def test_token_valido_retorna_payload(self):
        payload = {"sub": "10", "cargo": "diretor"}
        token = create_access_token(payload, expires_delta=timedelta(minutes=30))
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded["sub"] == "10"

    def test_token_expirado_retorna_none(self):
        payload = {"sub": "1"}
        token = create_access_token(payload, expires_delta=timedelta(seconds=-1))
        decoded = verify_token(token)
        assert decoded is None

    def test_token_invalido_retorna_none(self):
        decoded = verify_token("token.invalido.aqui")
        assert decoded is None

    def test_token_vazio_retorna_none(self):
        decoded = verify_token("")
        assert decoded is None


class TestValidatePasswordStrength:
    def test_senha_valida_retorna_true(self):
        assert validate_password_strength("Senha@123") is True

    def test_senha_com_todos_requisitos_retorna_true(self):
        assert validate_password_strength("Abc!1234") is True

    def test_sem_maiuscula_retorna_false(self):
        assert validate_password_strength("senha@123") is False

    def test_sem_minuscula_retorna_false(self):
        assert validate_password_strength("SENHA@123") is False

    def test_sem_numero_retorna_false(self):
        assert validate_password_strength("Senha@ABC") is False

    def test_sem_especial_retorna_false(self):
        assert validate_password_strength("Senha1234") is False

    def test_menos_de_8_caracteres_retorna_false(self):
        assert validate_password_strength("Ab@1") is False

    def test_senha_vazia_retorna_false(self):
        assert validate_password_strength("") is False