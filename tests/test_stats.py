from datetime import timedelta
from app.models import Link, Clique, utc_now

def test_estatisticas_sem_cliques(client, db_session):
    link = Link(
        codigo="stat01",
        url_original="https://example.com",
        criado_em=utc_now(),
        expira_em=utc_now() + timedelta(days=7),
        ativo=True
    )
    db_session.add(link)
    db_session.commit()

    response = client.get("/links/stat01/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo"] == "stat01"
    assert data["total_cliques"] == 0
    assert data["cliques_por_dia"] == {}
    assert data["cliques_por_dispositivo"] == {}
    assert len(data["ultimos_cliques"]) == 0

def test_estatisticas_com_multiplos_cliques(client, db_session):
    link = Link(
        codigo="stat02",
        url_original="https://github.com",
        criado_em=utc_now(),
        expira_em=utc_now() + timedelta(days=7),
        ativo=True
    )
    db_session.add(link)
    db_session.commit()

    c1 = Clique(
        link_id=link.id,
        acessado_em=utc_now(),
        ip="192.168.1.10",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        referer="https://google.com"
    )
    c2 = Clique(
        link_id=link.id,
        acessado_em=utc_now(),
        ip="192.168.1.20",
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        referer="https://t.co"
    )
    c3 = Clique(
        link_id=link.id,
        acessado_em=utc_now(),
        ip="66.249.66.1",
        user_agent="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        referer=None
    )
    db_session.add_all([c1, c2, c3])
    db_session.commit()

    response = client.get("/links/stat02/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_cliques"] == 3
    assert data["cliques_por_dispositivo"]["Desktop"] == 1
    assert data["cliques_por_dispositivo"]["Mobile"] == 1
    assert data["cliques_por_dispositivo"]["Bot / Crawler"] == 1
    assert len(data["ultimos_cliques"]) == 3

def test_estatisticas_link_inexistente_retorna_404(client):
    response = client.get("/links/nao_existe/stats")
    assert response.status_code == 404
