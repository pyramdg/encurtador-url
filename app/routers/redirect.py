from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Link
from app.services.tracking import extrair_ip_cliente, registrar_clique_background

router = APIRouter(tags=["Redirect"])

@router.get(
    "/{codigo}",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    summary="Redireciona da URL curta para a original",
    responses={
        302: {"description": "Redirecionamento temporário para a URL original"},
        404: {"description": "Link não encontrado ou inativo"},
        410: {"description": "Link expirado"}
    }
)
def redirecionar_link(
    codigo: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Busca o link pelo código curto indexado.
    - Se não existir ou inativo: 404 Not Found
    - Se data atual > expira_em: 410 Gone
    - Se válido: Agenda o rastreamento em segundo plano e retorna 302 Found imediatamente
    """
    link = db.query(Link).filter(Link.codigo == codigo, Link.ativo == True).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link curto não encontrado ou desativado."
        )

    if link.esta_expirado():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este link curto expirou e não está mais disponível."
        )

    # Extrai metadados da requisição
    ip = extrair_ip_cliente(request)
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")

    # Enfileira o registro do clique de forma assíncrona (não atrasa o redirect)
    background_tasks.add_task(
        registrar_clique_background,
        link_id=link.id,
        ip=ip,
        user_agent=user_agent,
        referer=referer
    )

    # Redirecionamento 302
    return RedirectResponse(
        url=link.url_original,
        status_code=status.HTTP_302_FOUND
    )
