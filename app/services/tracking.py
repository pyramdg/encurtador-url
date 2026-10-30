import logging
from typing import Optional
from fastapi import Request
from app.database import SessionLocal
from app.models import Clique, utc_now

logger = logging.getLogger(__name__)

def extrair_ip_cliente(request: Request) -> str:
    """Extrai o endereço IP real do cliente considerando proxies reversos (Traefik, Nginx, Cloudflare)."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Pega o primeiro IP da cadeia (cliente original)
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    
    if request.client and request.client.host:
        return request.client.host
    
    return "127.0.0.1"

def registrar_clique_background(
    link_id: int,
    ip: str,
    user_agent: Optional[str],
    referer: Optional[str]
):
    """
    Função executada em segundo plano (BackgroundTask) para persistir as métricas do clique
    sem adicionar latência ao redirecionamento 302 retornado ao usuário.
    """
    db = SessionLocal()
    try:
        novo_clique = Clique(
            link_id=link_id,
            acessado_em=utc_now(),
            ip=ip,
            user_agent=user_agent,
            referer=referer
        )
        db.add(novo_clique)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao registrar clique em background para link {link_id}: {e}")
    finally:
        db.close()
