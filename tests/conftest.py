import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
import app.services.tracking as tracking_service

# Banco de dados de teste em memória compartilhado via StaticPool
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sobrescreve tanto a dependência FastAPI quanto o SessionLocal das tarefas assíncronas
app.dependency_overrides[get_db] = override_get_db
tracking_service.SessionLocal = TestingSessionLocal

@pytest.fixture(autouse=True)
def init_test_db():
    """Garante tabelas criadas antes de cada teste e limpas após."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    """Fornece uma sessão direta para os testes manipularem o banco."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Fornece cliente HTTP de teste sem seguir redirects automaticamente."""
    return TestClient(app, follow_redirects=False)
