import pytest
from unittest.mock import MagicMock, patch, ANY
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
import jwt
from app.routers.auth_router import router
from app.schemas.auth_schema import LoginRequest, RefreshRequest, EsqueciSenhaRequest, RedefinirSenhaRequest
from app.schemas.usuario_schema import UsuarioUpdatePrimeiroAcesso
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.usuario_model import Usuario
from app.models.password_reset_model import PasswordResetToken


def create_mock_usuario(usuario_id=1, email="usuario@test.com", ativo=True, 
                        primeiro_acesso=False, cargo="operador", senha_hash=None):
    """Helper para criar usuários mock"""
    usuario = MagicMock(spec=Usuario)
    usuario.id = usuario_id
    usuario.email = email
    usuario.nome = "Usuário Teste"
    usuario.ativo = ativo
    usuario.primeiro_acesso = primeiro_acesso
    usuario.cargo = cargo
    usuario.senha = senha_hash or hash_password("Senha@123")
    return usuario


def create_mock_db():
    """Helper para criar database mock"""
    return MagicMock()


class TestLogin:
    """Testes para o endpoint POST /auth/login"""
    
    def test_login_com_credenciais_validas(self):
        """Testa login com email e senha corretos"""
        db = create_mock_db()
        usuario = create_mock_usuario(usuario_id=1, ativo=True, primeiro_acesso=False)
        db.query.return_value.filter.return_value.first.return_value = usuario
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.verify_password") as mock_verify:
                mock_obter.return_value = usuario
                mock_verify.return_value = True
                
                from app.routers.auth_router import login
                resultado = login(LoginRequest(email="usuario@test.com", password="Senha@123"), db)
                
                assert resultado.access_token is not None
                assert resultado.refresh_token is not None
                assert resultado.token_type == "bearer"
                assert resultado.primeiro_acesso is False

    def test_login_com_email_incorreto(self):
        """Testa login com email não existente"""
        db = create_mock_db()
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            mock_obter.return_value = None
            
            from app.routers.auth_router import login
            with pytest.raises(HTTPException) as exc:
                login(LoginRequest(email="naoexiste@test.com", password="Senha@123"), db)
            
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "E-mail ou senha incorretos" in str(exc.value.detail)

    def test_login_com_senha_incorreta(self):
        """Testa login com senha errada"""
        db = create_mock_db()
        usuario = create_mock_usuario()
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.verify_password") as mock_verify:
                mock_obter.return_value = usuario
                mock_verify.return_value = False
                
                from app.routers.auth_router import login
                with pytest.raises(HTTPException) as exc:
                    login(LoginRequest(email="usuario@test.com", password="SenhaErrada@1"), db)
                
                assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_com_usuario_inativo(self):
        """Testa login com usuário inativo"""
        db = create_mock_db()
        usuario = create_mock_usuario(ativo=False)
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.verify_password") as mock_verify:
                mock_obter.return_value = usuario
                mock_verify.return_value = True
                
                from app.routers.auth_router import login
                with pytest.raises(HTTPException) as exc:
                    login(LoginRequest(email="usuario@test.com", password="Senha@123"), db)
                
                assert exc.value.status_code == status.HTTP_403_FORBIDDEN
                assert "inativo" in str(exc.value.detail)

    def test_login_usuario_em_primeiro_acesso(self):
        """Testa login de usuário que nunca fez login"""
        db = create_mock_db()
        usuario = create_mock_usuario(primeiro_acesso=True)
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.verify_password") as mock_verify:
                mock_obter.return_value = usuario
                mock_verify.return_value = True
                
                from app.routers.auth_router import login
                resultado = login(LoginRequest(email="usuario@test.com", password="Senha@123"), db)
                
                assert resultado.primeiro_acesso is True
                assert resultado.access_token is not None

    def test_login_retorna_tokens_com_cargo_correto(self):
        """Testa se o token contém o cargo do usuário"""
        db = create_mock_db()
        usuario = create_mock_usuario(cargo="admin")
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.verify_password") as mock_verify:
                mock_obter.return_value = usuario
                mock_verify.return_value = True
                
                from app.routers.auth_router import login
                resultado = login(LoginRequest(email="usuario@test.com", password="Senha@123"), db)
                
                # Decodificar o token para verificar o cargo
                payload = jwt.decode(resultado.access_token, options={"verify_signature": False})
                assert payload["cargo"] == "admin"


class TestPrimeiroAcesso:
    """Testes para o endpoint POST /auth/primeiro-acesso"""
    
    def test_primeiro_acesso_com_senha_valida(self):
        """Testa definição de senha no primeiro acesso com senha válida"""
        db = create_mock_db()
        usuario = create_mock_usuario(primeiro_acesso=True)
        
        with patch("app.routers.auth_router.validate_password_strength") as mock_validate:
            with patch("app.routers.auth_router.hash_password") as mock_hash:
                mock_validate.return_value = True
                mock_hash.return_value = "hashed_password"
                
                from app.routers.auth_router import primeiro_acesso
                resultado = primeiro_acesso(
                    UsuarioUpdatePrimeiroAcesso(nova_senha="NovaSenha@123"),
                    db,
                    usuario
                )
                
                assert resultado["mensagem"] == "Senha definida com sucesso! Faça login novamente."
                assert usuario.primeiro_acesso is False
                db.commit.assert_called_once()

    def test_primeiro_acesso_usuario_ja_acessou(self):
        """Testa se impede primeiro acesso para usuário que já acessou"""
        db = create_mock_db()
        usuario = create_mock_usuario(primeiro_acesso=False)
        
        from app.routers.auth_router import primeiro_acesso
        with pytest.raises(HTTPException) as exc:
            primeiro_acesso(
                UsuarioUpdatePrimeiroAcesso(nova_senha="NovaSenha@123"),
                db,
                usuario
            )
        
        assert exc.value.status_code == 400
        assert "já realizou o primeiro acesso" in str(exc.value.detail)

    def test_primeiro_acesso_com_senha_fraca(self):
        """Testa primeiro acesso com senha que não atende requisitos"""
        db = create_mock_db()
        usuario = create_mock_usuario(primeiro_acesso=True)
        
        with patch("app.routers.auth_router.validate_password_strength") as mock_validate:
            mock_validate.return_value = False
            
            from app.routers.auth_router import primeiro_acesso
            with pytest.raises(HTTPException) as exc:
                primeiro_acesso(
                    UsuarioUpdatePrimeiroAcesso(nova_senha="fraca"),
                    db,
                    usuario
                )
            
            assert exc.value.status_code == 400
            assert "não atende aos requisitos" in str(exc.value.detail)


class TestRefresh:
    """Testes para o endpoint POST /auth/refresh"""
    
    def test_refresh_token_valido(self):
        """Testa geração de novo access token com refresh token válido"""
        db = create_mock_db()
        usuario = create_mock_usuario(usuario_id=1, ativo=True)
        
        # Criar um refresh token válido
        refresh_payload = {"sub": "1"}
        refresh_token = create_refresh_token(refresh_payload)
        
        # Mock do query
        db.query.return_value.filter.return_value.first.return_value = usuario
        
        with patch("app.routers.auth_router.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "1", "type": "refresh"}
            
            from app.routers.auth_router import refresh
            resultado = refresh(RefreshRequest(refresh_token=refresh_token), db)
            
            assert resultado.access_token is not None
            assert resultado.refresh_token is not None
            assert resultado.token_type == "bearer"

    def test_refresh_token_invalido(self):
        """Testa refresh com token inválido"""
        db = create_mock_db()
        
        with patch("app.routers.auth_router.verify_token") as mock_verify:
            mock_verify.return_value = None
            
            from app.routers.auth_router import refresh
            with pytest.raises(HTTPException) as exc:
                refresh(RefreshRequest(refresh_token="token_invalido"), db)
            
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "inválido" in str(exc.value.detail)

    def test_refresh_token_com_tipo_errado(self):
        """Testa refresh com token que não é do tipo 'refresh'"""
        db = create_mock_db()
        
        with patch("app.routers.auth_router.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "1", "type": "access"}
            
            from app.routers.auth_router import refresh
            with pytest.raises(HTTPException) as exc:
                refresh(RefreshRequest(refresh_token="token_access"), db)
            
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_usuario_nao_existe(self):
        """Testa refresh quando usuário não existe mais"""
        db = create_mock_db()
        db.query.return_value.filter.return_value.first.return_value = None
        
        with patch("app.routers.auth_router.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "999", "type": "refresh"}
            
            from app.routers.auth_router import refresh
            with pytest.raises(HTTPException) as exc:
                refresh(RefreshRequest(refresh_token="token"), db)
            
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_usuario_inativo(self):
        """Testa refresh quando usuário está inativo"""
        db = create_mock_db()
        usuario = create_mock_usuario(ativo=False)
        db.query.return_value.filter.return_value.first.return_value = usuario
        
        with patch("app.routers.auth_router.verify_token") as mock_verify:
            mock_verify.return_value = {"sub": "1", "type": "refresh"}
            
            from app.routers.auth_router import refresh
            with pytest.raises(HTTPException) as exc:
                refresh(RefreshRequest(refresh_token="token"), db)
            
            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "inativo" in str(exc.value.detail)


class TestEsqueciSenha:
    """Testes para o endpoint POST /auth/esqueci-senha"""
    
    def test_esqueci_senha_email_valido(self):
        """Testa requisição de recuperação de senha com email válido"""
        db = create_mock_db()
        usuario = create_mock_usuario(ativo=True)
        
        # Mock dos queries
        db.query.return_value.filter.return_value.delete.return_value = None
        db.query.return_value.filter.return_value = MagicMock()
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.enviar_email_recuperacao") as mock_email:
                mock_obter.return_value = usuario
                
                from app.routers.auth_router import esqueci_senha
                resultado = esqueci_senha(EsqueciSenhaRequest(email="usuario@test.com"), db)
                
                assert "mensagem" in resultado
                db.add.assert_called_once()
                db.commit.assert_called()
                mock_email.assert_called_once()

    def test_esqueci_senha_email_nao_existe(self):
        """Testa requisiçãocom email não cadastrado (deve retornar mensagem genérica)"""
        db = create_mock_db()
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            mock_obter.return_value = None
            
            from app.routers.auth_router import esqueci_senha
            resultado = esqueci_senha(EsqueciSenhaRequest(email="naoexiste@test.com"), db)
            
            # Deve retornar mensagem genérica por segurança
            assert "mensagem" in resultado
            assert "Se o e-mail estiver cadastrado" in resultado["mensagem"]
            db.add.assert_not_called()

    def test_esqueci_senha_usuario_inativo(self):
        """Testa requisição com usuário inativo (deve retornar mensagem genérica)"""
        db = create_mock_db()
        usuario = create_mock_usuario(ativo=False)
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            mock_obter.return_value = usuario
            
            from app.routers.auth_router import esqueci_senha
            resultado = esqueci_senha(EsqueciSenhaRequest(email="inativo@test.com"), db)
            
            assert "mensagem" in resultado
            db.add.assert_not_called()

    def test_esqueci_senha_limpa_tokens_antigos(self):
        """Testa se limpa tokens de recuperação antigos"""
        db = create_mock_db()
        usuario = create_mock_usuario(ativo=True)
        
        db.query.return_value.filter.return_value.delete.return_value = 1  # 1 token deletado
        
        with patch("app.routers.auth_router.obter_usuario_por_email") as mock_obter:
            with patch("app.routers.auth_router.enviar_email_recuperacao"):
                mock_obter.return_value = usuario
                
                from app.routers.auth_router import esqueci_senha
                esqueci_senha(EsqueciSenhaRequest(email="usuario@test.com"), db)
                
                # Verifica se foi chamado delete
                db.query.assert_called()


class TestRedefinirSenha:
    """Testes para o endpoint POST /auth/redefinir-senha"""
    
    def test_redefinir_senha_token_valido(self):
        """Testa redefinição de senha com token válido"""
        db = create_mock_db()
        usuario = create_mock_usuario()
        
        # Criar token mock
        agora = datetime.now(timezone.utc)
        reset_token = MagicMock(spec=PasswordResetToken)
        reset_token.token = "token_valido"
        reset_token.usuario = usuario
        reset_token.expira_em = agora + timedelta(minutes=15)
        reset_token.usado = False
        
        db.query.return_value.filter.return_value.first.return_value = reset_token
        
        with patch("app.routers.auth_router.validate_password_strength") as mock_validate:
            with patch("app.routers.auth_router.hash_password") as mock_hash:
                mock_validate.return_value = True
                mock_hash.return_value = "hashed_new_password"
                
                from app.routers.auth_router import redefinir_senha
                resultado = redefinir_senha(
                    RedefinirSenhaRequest(token="token_valido", nova_senha="NovaSenha@123"),
                    db
                )
                
                assert resultado["mensagem"] == "Senha redefinida com sucesso!"
                assert reset_token.usado is True
                db.commit.assert_called()

    def test_redefinir_senha_token_nao_existe(self):
        """Testa redefinição com token inexistente"""
        db = create_mock_db()
        db.query.return_value.filter.return_value.first.return_value = None
        
        from app.routers.auth_router import redefinir_senha
        with pytest.raises(HTTPException) as exc:
            redefinir_senha(
                RedefinirSenhaRequest(token="token_invalido", nova_senha="NovaSenha@123"),
                db
            )
        
        assert exc.value.status_code == 400
        assert "inválido" in str(exc.value.detail)

    def test_redefinir_senha_token_expirado(self):
        """Testa redefinição com token expirado"""
        db = create_mock_db()
        usuario = create_mock_usuario()
        
        # Token expirado
        agora = datetime.now(timezone.utc)
        reset_token = MagicMock(spec=PasswordResetToken)
        reset_token.expira_em = agora - timedelta(minutes=5)
        reset_token.usado = False
        
        db.query.return_value.filter.return_value.first.return_value = reset_token
        
        from app.routers.auth_router import redefinir_senha
        with pytest.raises(HTTPException) as exc:
            redefinir_senha(
                RedefinirSenhaRequest(token="token_expirado", nova_senha="NovaSenha@123"),
                db
            )
        
        assert exc.value.status_code == 400
        assert "expirado" in str(exc.value.detail)

    def test_redefinir_senha_token_ja_utilizado(self):
        """Testa redefinição com token já utilizado"""
        db = create_mock_db()
        
        reset_token = MagicMock(spec=PasswordResetToken)
        reset_token.token = "token_usado"
        reset_token.usado = True
        
        db.query.return_value.filter.return_value.first.return_value = None
        
        from app.routers.auth_router import redefinir_senha
        with pytest.raises(HTTPException) as exc:
            redefinir_senha(
                RedefinirSenhaRequest(token="token_usado", nova_senha="NovaSenha@123"),
                db
            )
        
        assert exc.value.status_code == 400

    def test_redefinir_senha_fraca(self):
        """Testa redefinição com senha que não atende requisitos"""
        db = create_mock_db()
        usuario = create_mock_usuario()
        
        agora = datetime.now(timezone.utc)
        reset_token = MagicMock(spec=PasswordResetToken)
        reset_token.expira_em = agora + timedelta(minutes=15)
        reset_token.usuario = usuario
        reset_token.usado = False
        
        db.query.return_value.filter.return_value.first.return_value = reset_token
        
        with patch("app.routers.auth_router.validate_password_strength") as mock_validate:
            mock_validate.return_value = False
            
            from app.routers.auth_router import redefinir_senha
            with pytest.raises(HTTPException) as exc:
                redefinir_senha(
                    RedefinirSenhaRequest(token="token_valido", nova_senha="fraca"),
                    db
                )
            
            assert exc.value.status_code == 400
            assert "não atende aos requisitos" in str(exc.value.detail)

    def test_redefinir_senha_com_timezone_ingenue(self):
        """Testa se função trata corretamente datetime sem timezone"""
        db = create_mock_db()
        usuario = create_mock_usuario()
        
        # Token com datetime sem timezone
        agora = datetime.now()  # sem timezone
        reset_token = MagicMock(spec=PasswordResetToken)
        reset_token.expira_em = agora + timedelta(minutes=15)
        reset_token.usuario = usuario
        reset_token.usado = False
        reset_token.token = "token_valido"
        
        db.query.return_value.filter.return_value.first.return_value = reset_token
        
        with patch("app.routers.auth_router.validate_password_strength") as mock_validate:
            with patch("app.routers.auth_router.hash_password"):
                mock_validate.return_value = True
                
                from app.routers.auth_router import redefinir_senha
                # Não deve lançar erro
                resultado = redefinir_senha(
                    RedefinirSenhaRequest(token="token_valido", nova_senha="NovaSenha@123"),
                    db
                )
                
                assert resultado["mensagem"] == "Senha redefinida com sucesso!"
