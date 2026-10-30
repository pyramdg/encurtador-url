from collections import Counter
from typing import Dict, List
import user_agents
from sqlalchemy.orm import Session
from app.models import Link, Clique
from app.schemas import StatsResponse, CliqueDetalhe
from app.config import settings

def parse_user_agent(ua_string: str) -> tuple[str, str]:
    """Interpreta a string de User-Agent retornando (dispositivo, navegador)."""
    if not ua_string:
        return ("Desconhecido", "Desconhecido")
    try:
        ua = user_agents.parse(ua_string)
        if ua.is_bot:
            device = "Bot / Crawler"
        elif ua.is_mobile:
            device = "Mobile"
        elif ua.is_tablet:
            device = "Tablet"
        elif ua.is_pc:
            device = "Desktop"
        else:
            device = "Outro"
            
        browser = ua.browser.family if ua.browser.family else "Outro"
        return (device, browser)
    except Exception:
        return ("Desconhecido", "Desconhecido")

def obter_estatisticas_link(link: Link, db: Session) -> StatsResponse:
    """Calcula e formata as métricas agregadas do link curto."""
    cliques: List[Clique] = db.query(Clique).filter(Clique.link_id == link.id).order_by(Clique.acessado_em.desc()).all()

    total_cliques = len(cliques)
    cliques_por_dia: Dict[str, int] = Counter()
    cliques_por_dispositivo: Dict[str, int] = Counter()
    cliques_por_navegador: Dict[str, int] = Counter()
    ultimos_cliques: List[CliqueDetalhe] = []

    for c in cliques:
        dia_str = c.acessado_em.strftime("%Y-%m-%d")
        cliques_por_dia[dia_str] += 1

        device, browser = parse_user_agent(c.user_agent or "")
        cliques_por_dispositivo[device] += 1
        cliques_por_navegador[browser] += 1

        if len(ultimos_cliques) < 20:
            ultimos_cliques.append(CliqueDetalhe(
                acessado_em=c.acessado_em,
                ip=c.ip,
                user_agent=c.user_agent,
                referer=c.referer,
                dispositivo=device,
                navegador=browser
            ))

    # Ordena os dias cronologicamente
    dias_ordenados = dict(sorted(cliques_por_dia.items()))

    url_curta = f"{settings.BASE_URL.rstrip('/')}/{link.codigo}"

    return StatsResponse(
        codigo=link.codigo,
        url_original=link.url_original,
        url_curta=url_curta,
        criado_em=link.criado_em,
        expira_em=link.expira_em,
        ativo=link.ativo,
        expirado=link.esta_expirado(),
        total_cliques=total_cliques,
        cliques_por_dia=dias_ordenados,
        cliques_por_dispositivo=dict(cliques_por_dispositivo),
        cliques_por_navegador=dict(cliques_por_navegador),
        ultimos_cliques=ultimos_cliques
    )
