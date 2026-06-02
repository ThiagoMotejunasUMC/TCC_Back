import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.crud.crud_usuario import (
    criar_usuario, listar_usuarios, obter_usuario_por_id,
    obter_usuario_por_email, atualizar_usuario,
    atualizar_senha, deletar_usuario
)
from app.schemas.usuario_schema import UsuarioCreate, UsuarioUpdate, UsuarioUpdateSenha


def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.offset.return_value.limit.return_value.all.return_value = []
    return db


class TestCriarUsuario:
    def test_cria_com_senha_valida(self):
        db = mock_db()
        data = UsuarioCreate(nome="João", email="joao@sge.com", senha="Senha@123", cargo="operador")
        with patch("app.crud.crud_usuario.registrar_log"):
            criar_usuario(db, data, usuario_id=1)
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_erro_senha_fraca_no_schema(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(nome="João", email="joao@sge.com", senha="fraca", cargo="operador")

    def test_erro_email_duplicado(self):
        db = mock_db()
        db.query.return_value.filter.return_value.first.return_value = MagicMock()
        data = UsuarioCreate(nome="João", email="joao@sge.com", senha="Senha@123", cargo="operador")
        with pytest.raises(HTTPException) as exc:
            criar_usuario(db, data, usuario_id=1)
        assert exc.value.status_code == 400

    def test_senha_armazenada_como_hash(self):
        db = mock_db()
        data = UsuarioCreate(nome="João", email="joao@sge.com", senha="Senha@123", cargo="operador")
        with patch("app.crud.crud_usuario.registrar_log"):
            criar_usuario(db, data, usuario_id=1)
        usuario_criado = db.add.call_args[0][0]
        assert usuario_criado.senha != "Senha@123"

    def test_cria_sem_usuario_id_nao_loga(self):
        db = mock_db()
        data = UsuarioCreate(nome="João", email="joao@sge.com", senha="Senha@123", cargo="operador")
        with patch("app.crud.crud_usuario.registrar_log") as mock_log:
            criar_usuario(db, data)
        mock_log.assert_not_called()


class TestListarUsuarios:
    def test_lista_todos(self):
        db = mock_db()
        resultado = listar_usuarios(db)
        assert isinstance(resultado, list)

    def test_lista_com_paginacao(self):
        db = mock_db()
        resultado = listar_usuarios(db, skip=0, limit=10)
        assert isinstance(resultado, list)


class TestObterUsuarioPorId:
    def test_retorna_usuario_existente(self):
        db = mock_db()
        usuario_mock = MagicMock(id=1, nome="João")
        db.query.return_value.filter.return_value.first.return_value = usuario_mock
        resultado = obter_usuario_por_id(db, 1)
        assert resultado.nome == "João"

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        resultado = obter_usuario_por_id(db, 999)
        assert resultado is None


class TestObterUsuarioPorEmail:
    def test_retorna_usuario_existente(self):
        db = mock_db()
        usuario_mock = MagicMock(id=1, email="joao@sge.com")
        db.query.return_value.filter.return_value.first.return_value = usuario_mock
        resultado = obter_usuario_por_email(db, "joao@sge.com")
        assert resultado.email == "joao@sge.com"

    def test_retorna_none_nao_encontrado(self):
        db = mock_db()
        resultado = obter_usuario_por_email(db, "naoexiste@sge.com")
        assert resultado is None


class TestAtualizarUsuario:
    def test_atualiza_nome(self):
        db = mock_db()
        usuario_mock = MagicMock(id=1, nome="João")
        db.query.return_value.filter.return_value.first.return_value = usuario_mock
        data = UsuarioUpdate(nome="João Silva")
        with patch("app.crud.crud_usuario.registrar_log"):
            atualizar_usuario(db, 1, data, executor_id=2)
        assert usuario_mock.nome == "João Silva"

    def test_erro_usuario_nao_encontrado(self):
        db = mock_db()
        data = UsuarioUpdate(nome="Novo")
        with pytest.raises(HTTPException) as exc:
            atualizar_usuario(db, 999, data)
        assert exc.value.status_code == 404

    def test_atualiza_sem_executor_id_nao_loga(self):
        db = mock_db()
        usuario_mock = MagicMock(id=1, nome="João")
        db.query.return_value.filter.return_value.first.return_value = usuario_mock
        data = UsuarioUpdate(nome="João Silva")
        with patch("app.crud.crud_usuario.registrar_log") as mock_log:
            atualizar_usuario(db, 1, data)
        mock_log.assert_not_called()


class TestAtualizarSenha:
    def test_atualiza_com_senha_atual_correta(self):
        from app.core.security import hash_password
        db = mock_db()
        usuario_mock = MagicMock()
        usuario_mock.senha = hash_password("SenhaAtual@1")
        data = UsuarioUpdateSenha(senha_atual="SenhaAtual@1", nova_senha="NovaSenha@2")
        with patch("app.crud.crud_usuario.registrar_log"):
            atualizar_senha(db, usuario_mock, data)
        db.commit.assert_called_once()

    def test_erro_senha_atual_incorreta(self):
        from app.core.security import hash_password
        db = mock_db()
        usuario_mock = MagicMock()
        usuario_mock.senha = hash_password("SenhaCorreta@1")
        data = UsuarioUpdateSenha(senha_atual="SenhaErrada@1", nova_senha="NovaSenha@2")
        with pytest.raises(HTTPException) as exc:
            atualizar_senha(db, usuario_mock, data)
        assert exc.value.status_code == 400

    def test_erro_nova_senha_fraca_no_schema(self):
        with pytest.raises(ValidationError):
            UsuarioUpdateSenha(senha_atual="SenhaAtual@1", nova_senha="fraca")


class TestDeletarUsuario:
    def test_desativa_usuario(self):
        db = mock_db()
        usuario_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = usuario_mock
        with patch("app.crud.crud_usuario.registrar_log"):
            deletar_usuario(db, 1, executor_id=2)
        assert usuario_mock.ativo is False

    def test_erro_usuario_nao_encontrado(self):
        db = mock_db()
        with pytest.raises(HTTPException) as exc:
            deletar_usuario(db, 999)
        assert exc.value.status_code == 404

    def test_deleta_sem_executor_id_nao_loga(self):
        db = mock_db()
        usuario_mock = MagicMock(id=1, ativo=True)
        db.query.return_value.filter.return_value.first.return_value = usuario_mock
        with patch("app.crud.crud_usuario.registrar_log") as mock_log:
            deletar_usuario(db, 1)
        mock_log.assert_not_called()