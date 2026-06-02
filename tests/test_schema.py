import pytest
from pydantic import ValidationError
from app.schemas.usuario_schema import (
    UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha,
    UsuarioUpdatePrimeiroAcesso, validar_senha
)


class TestValidarSenha:
    def test_senha_valida(self):
        assert validar_senha("Senha@123") == "Senha@123"

    def test_sem_maiuscula_levanta_erro(self):
        with pytest.raises(ValueError, match="maiúscula"):
            validar_senha("senha@123")

    def test_sem_minuscula_levanta_erro(self):
        with pytest.raises(ValueError, match="minúscula"):
            validar_senha("SENHA@123")

    def test_sem_numero_levanta_erro(self):
        with pytest.raises(ValueError, match="número"):
            validar_senha("Senha@ABC")

    def test_sem_especial_levanta_erro(self):
        with pytest.raises(ValueError, match="especial"):
            validar_senha("Senha1234")

    def test_menos_8_caracteres_levanta_erro(self):
        with pytest.raises(ValueError, match="8 caracteres"):
            validar_senha("Ab@1")

    def test_senha_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            validar_senha("")


class TestUsuarioCreate:
    def test_cria_com_dados_validos(self):
        usuario = UsuarioCreate(
            nome="João Silva",
            email="joao@sge.com",
            senha="Senha@123",
            cargo="operador"
        )
        assert usuario.nome == "João Silva"
        assert usuario.cargo == "operador"

    def test_cargo_padrao_operador(self):
        usuario = UsuarioCreate(
            nome="João",
            email="joao@sge.com",
            senha="Senha@123"
        )
        assert usuario.cargo == "operador"

    def test_erro_senha_fraca(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="João", email="joao@sge.com", senha="fraca")

    def test_erro_email_invalido(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="João", email="emailinvalido", senha="Senha@123")

    def test_validator_senha_forte_chamado(self):
        with pytest.raises(ValidationError) as exc:
            UsuarioCreate(nome="João", email="joao@sge.com", senha="semmaius1@")
        assert "maiúscula" in str(exc.value)


class TestUsuarioUpdate:
    def test_todos_campos_opcionais(self):
        update = UsuarioUpdate()
        assert update.nome is None
        assert update.email is None
        assert update.cargo is None
        assert update.ativo is None

    def test_atualiza_apenas_nome(self):
        update = UsuarioUpdate(nome="Novo Nome")
        assert update.nome == "Novo Nome"
        assert update.cargo is None

    def test_atualiza_ativo_false(self):
        update = UsuarioUpdate(ativo=False)
        assert update.ativo is False


class TestUsuarioUpdateSenha:
    def test_cria_com_dados_validos(self):
        data = UsuarioUpdateSenha(
            senha_atual="SenhaAtual@1",
            nova_senha="NovaSenha@2"
        )
        assert data.senha_atual == "SenhaAtual@1"

    def test_erro_nova_senha_fraca(self):
        with pytest.raises(ValidationError):
            UsuarioUpdateSenha(senha_atual="SenhaAtual@1", nova_senha="fraca")

    def test_validator_nova_senha_sem_maiuscula(self):
        with pytest.raises(ValidationError) as exc:
            UsuarioUpdateSenha(senha_atual="SenhaAtual@1", nova_senha="novasenha@1")
        assert "maiúscula" in str(exc.value)

    def test_validator_nova_senha_sem_especial(self):
        with pytest.raises(ValidationError) as exc:
            UsuarioUpdateSenha(senha_atual="SenhaAtual@1", nova_senha="NovaSenha1")
        assert "especial" in str(exc.value)


class TestUsuarioUpdatePrimeiroAcesso:
    def test_cria_com_senha_valida(self):
        data = UsuarioUpdatePrimeiroAcesso(nova_senha="Senha@123")
        assert data.nova_senha == "Senha@123"

    def test_erro_senha_fraca(self):
        with pytest.raises(ValidationError):
            UsuarioUpdatePrimeiroAcesso(nova_senha="fraca")

    def test_validator_sem_numero(self):
        with pytest.raises(ValidationError) as exc:
            UsuarioUpdatePrimeiroAcesso(nova_senha="Senha@ABC")
        assert "número" in str(exc.value)