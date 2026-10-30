from datetime import timedelta
from app.models import Link, utc_now

def test_fluxo_completo_encurtar_redirecionar_e_estatisticas(client, db_session):
    # 1. Encurtar URL longa
    original_url = "https://news.ycombinator.com/item?id=400000"
    res_create = client.post("/links", json={
        "url": original_url,
        "dias_validade": 30
    })
    assert res_create.status_code == 201
    link_data = res_create.json()
    codigo = link_data["codigo"]
    assert link_data["url_original"] == original_url

    # 2. Acessar a URL curta 2 vezes com navegadores diferentes
    headers_chrome = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://linkedin.com",
        "X-Forwarded-For": "203.0.113.195"
    }
    res_click1 = client.get(f"/{codigo}", headers=headers_chrome)
    assert res_click1.status_code == 302
    assert res_click1.headers["location"] == original_url

    headers_mobile = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Referer": "https://whatsapp.com",
        "X-Forwarded-For": "198.51.100.4"
    }
    res_click2 = client.get(f"/{codigo}", headers=headers_mobile)
    assert res_click2.status_code == 302
    assert res_click2.headers["location"] == original_url

    # 3. Consultar as estatísticas e verificar persistência dos cliques
    res_stats = client.get(f"/links/{codigo}/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_cliques"] == 2
    assert stats["cliques_por_dispositivo"]["Desktop"] == 1
    assert stats["cliques_por_dispositivo"]["Mobile"] == 1
    assert stats["cliques_por_navegador"]["Chrome"] == 1
    assert stats["cliques_por_navegador"]["Mobile Safari"] == 1

    # 4. Simular link expirado e verificar bloqueio com 410
    link_db = db_session.query(Link).filter(Link.codigo == codigo).first()
    link_db.expira_em = utc_now() - timedelta(minutes=1)
    db_session.commit()

    res_expired = client.get(f"/{codigo}")
    assert res_expired.status_code == 410
