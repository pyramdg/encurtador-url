from app.models import Link, Clique, utc_now
from datetime import timedelta

def test_create_tables_and_models(db_session):
    agora = utc_now()
    expira = agora + timedelta(days=7)
    link = Link(
        codigo="teste12",
        url_original="https://google.com",
        criado_em=agora,
        expira_em=expira,
        ativo=True
    )
    db_session.add(link)
    db_session.commit()
    db_session.refresh(link)

    assert link.id is not None
    assert link.codigo == "teste12"
    assert not link.esta_expirado()

    clique = Clique(
        link_id=link.id,
        acessado_em=utc_now(),
        ip="127.0.0.1",
        user_agent="Mozilla/5.0 Test",
        referer="https://twitter.com"
    )
    db_session.add(clique)
    db_session.commit()
    db_session.refresh(clique)

    assert clique.id is not None
    assert clique.link_id == link.id
    assert len(link.cliques) == 1
