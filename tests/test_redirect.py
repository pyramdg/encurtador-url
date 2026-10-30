from datetime import timedelta
from app.models import Link, utc_now

def test_redirecionamento_sucesso(client, db_session):
    link = Link(
        codigo="red123",
        url_original="https://antigravity.google.com/docs",
        criado_em=utc_now(),
        expira_em=utc_now() + timedelta(days=7),
        ativo=True
    )
    db_session.add(link)
    db_session.commit()

    response = client.get("/red123")
    assert response.status_code == 302
    assert response.headers["location"] == "https://antigravity.google.com/docs"

def test_redirecionamento_codigo_inexistente_retorna_404(client):
    response = client.get("/naoexiste99")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

def test_redirecionamento_link_inativo_retorna_404(client, db_session):
    link = Link(
        codigo="desativado",
        url_original="https://google.com",
        criado_em=utc_now(),
        expira_em=utc_now() + timedelta(days=7),
        ativo=False
    )
    db_session.add(link)
    db_session.commit()

    response = client.get("/desativado")
    assert response.status_code == 404

def test_redirecionamento_link_expirado_retorna_410(client, db_session):
    link = Link(
        codigo="expirado1",
        url_original="https://google.com",
        criado_em=utc_now() - timedelta(days=5),
        expira_em=utc_now() - timedelta(days=1),
        ativo=True
    )
    db_session.add(link)
    db_session.commit()

    response = client.get("/expirado1")
    assert response.status_code == 410
    assert "expirou" in response.json()["detail"]
