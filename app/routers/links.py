from datetime import timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Link, utc_now
from app.schemas import LinkCreate, LinkResponse, StatsResponse
from app.services.shortener import get_unique_short_code
from app.services.stats import obter_estatisticas_link
from app.config import settings

router = APIRouter(tags=["Links"])

def format_link_response(link: Link) -> LinkResponse:
    url_curta = f"{settings.BASE_URL.rstrip('/')}/{link.codigo}"
    return LinkResponse(
        id=link.id,
        codigo=link.codigo,
        url_original=link.url_original,
        url_curta=url_curta,
        criado_em=link.criado_em,
        expira_em=link.expira_em,
        ativo=link.ativo
    )

@router.post("/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED, summary="Criar link curto")
@router.post("/api/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def criar_link_curto(payload: LinkCreate, db: Session = Depends(get_db)):
    """
    Cria um link curto a partir de uma URL original válida.
    - Validação de protocolo HTTP/HTTPS.
    - Suporta expiração customizada ou padrão (ex: 7 dias).
    - Suporta alias personalizado opcional (/meu-link).
    """
    agora = utc_now()

    # Cálculo da data de expiração
    if payload.expira_em is not None:
        expira_em = payload.expira_em
        if expira_em.tzinfo is None:
            expira_em = expira_em.replace(tzinfo=timezone.utc)
        if expira_em <= agora:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A data de expiração deve ser no futuro."
            )
    elif payload.dias_validade is not None:
        if payload.dias_validade <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Os dias de validade devem ser maiores que zero."
            )
        expira_em = agora + timedelta(days=payload.dias_validade)
    else:
        # Padrão: 7 dias
        expira_em = agora + timedelta(days=settings.DEFAULT_EXPIRATION_DAYS)

    # Definição do código
    if payload.custom_alias:
        existente = db.query(Link).filter(Link.codigo == payload.custom_alias).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"O alias '{payload.custom_alias}' já está em uso. Escolha outro."
            )
        codigo = payload.custom_alias
    else:
        codigo = get_unique_short_code(db, length=settings.SHORT_CODE_MIN_LENGTH)

    novo_link = Link(
        codigo=codigo,
        url_original=str(payload.url),
        criado_em=agora,
        expira_em=expira_em,
        ativo=True
    )

    db.add(novo_link)
    db.commit()
    db.refresh(novo_link)

    return format_link_response(novo_link)

@router.get("/links/{codigo}/stats", response_model=StatsResponse, summary="Obter estatísticas de um link")
@router.get("/api/links/{codigo}/stats", response_model=StatsResponse, include_in_schema=False)
def ver_estatisticas(codigo: str, db: Session = Depends(get_db)):
    """
    Retorna métricas consolidadas do link:
    - Total de cliques
    - Cliques agrupados por dia
    - Cliques agrupados por tipo de dispositivo (Mobile, Desktop, etc.)
    - Cliques agrupados por navegador
    - Histórico detalhado dos últimos acessos
    """
    link = db.query(Link).filter(Link.codigo == codigo).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link não encontrado."
        )

    return obter_estatisticas_link(link, db)
