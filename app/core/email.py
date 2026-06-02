import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def enviar_email_recuperacao(email_destino: str, nome: str, token: str):
    link = f"{settings.FRONTEND_URL}/redefinir-senha?token={token}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0f62fe;">SGE — Recuperação de Senha</h2>
        <p>Olá, <strong>{nome}</strong>!</p>
        <p>Foi solicitada a recuperação de senha para sua conta no SGE.</p>
        <p>Clique no botão abaixo para redefinir sua senha:</p>
        <a href="{link}" style="display:inline-block;background:#0f62fe;color:#fff;padding:12px 24px;text-decoration:none;margin:16px 0;">Redefinir Senha</a>
        <p style="color:#666;font-size:14px;">Este link expira em 30 minutos.</p>
    </div>
    """
    _enviar_email(email_destino, "SGE — Recuperação de Senha", html_content)

def enviar_email_primeiro_acesso(email_destino: str, nome: str):
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #0f62fe;">SGE — Bem-vindo ao sistema!</h2>
        <p>Olá, <strong>{nome}</strong>!</p>
        <p>Sua conta foi criada no SGE — Sistema de Gerenciamento de Estoque.</p>
        <p>Por segurança, você será solicitado a definir uma nova senha no seu primeiro acesso.</p>
        <p style="color:#666;font-size:14px;">Acesse o sistema com as credenciais fornecidas pelo administrador e siga as instruções para definir sua senha.</p>
    </div>
    """
    _enviar_email(email_destino, "SGE — Bem-vindo ao sistema", html_content)

def enviar_email_alerta_estoque(email_destino: str, nome: str, produto_nome: str, quantidade: int, minimo: int):
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #da1e28;">SGE — Alerta de Estoque Mínimo</h2>
        <p>Olá, <strong>{nome}</strong>!</p>
        <p>O produto <strong>{produto_nome}</strong> atingiu o nível mínimo de estoque.</p>
        <div style="background:#fff1f1;border-left:4px solid #da1e28;padding:16px;margin:16px 0;">
            <p style="margin:0;font-size:14px;"><strong>Produto:</strong> {produto_nome}</p>
            <p style="margin:4px 0;font-size:14px;"><strong>Disponível:</strong> {quantidade} unidade(s)</p>
            <p style="margin:4px 0;font-size:14px;"><strong>Estoque mínimo:</strong> {minimo} unidade(s)</p>
        </div>
        <p>Acesse o SGE para verificar e tomar as providências necessárias.</p>
    </div>
    """
    _enviar_email(email_destino, f"SGE — Alerta de Estoque: {produto_nome}", html_content)

def _enviar_email(email_destino: str, assunto: str, html_content: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = assunto
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = email_destino
        msg.attach(MIMEText(html_content, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, email_destino, msg.as_string())
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail para {email_destino}: {e}")
        return False