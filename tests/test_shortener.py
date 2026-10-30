from datetime import timedelta
from app.models import utc_now

def test_criar_link_sucesso(client):
    response = client.post("/links", json={"url": "https://google.com"})
    assert response.status_code == 201
    data = response.json()
    assert "codigo" in data
    assert len(data["codigo"]) == 6
    assert data["url_original"] == "https://google.com"
    assert data["url_curta"].endswith(data["codigo"])
    assert data["ativo"] is True
    assert data["expira_em"] is not None

def test_validacao_url_invalida(client):
    response = client.post("/links", json={"url": "ftp://google.com"})
    assert response.status_code == 422

    response2 = client.post("/links", json={"url": "not-a-url"})
    assert response2.status_code == 422

def test_criar_link_com_alias_personalizado(client):
    response = client.post("/links", json={
        "url": "https://github.com/my-repo",
        "custom_alias": "meu-repositorio"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == "meu-repositorio"
    assert data["url_curta"].endswith("/meu-repositorio")

def test_criar_link_alias_duplicado_retorna_409(client):
    client.post("/links", json={
        "url": "https://github.com/my-repo",
        "custom_alias": "link-duplicado"
    })
    response2 = client.post("/links", json={
        "url": "https://outra-url.com",
        "custom_alias": "link-duplicado"
    })
    assert response2.status_code == 409
    assert "já está em uso" in response2.json()["detail"]

def test_criar_link_com_dias_validade(client):
    response = client.post("/links", json={
        "url": "https://google.com",
        "dias_validade": 15
    })
    assert response.status_code == 201
    data = response.json()
    assert data["expira_em"] is not None

def test_criar_link_expiracao_no_passado_retorna_400(client):
    passado = (utc_now() - timedelta(days=1)).isoformat()
    response = client.post("/links", json={
        "url": "https://google.com",
        "expira_em": passado
    })
    assert response.status_code == 400
    assert "deve ser no futuro" in response.json()["detail"]
