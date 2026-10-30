from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(20), unique=True, index=True, nullable=False)
    url_original = Column(Text, nullable=False)
    criado_em = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expira_em = Column(DateTime(timezone=True), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamento com os cliques
    cliques = relationship("Clique", back_populates="link", cascade="all, delete-orphan")

    def esta_expirado(self) -> bool:
        if self.expira_em is None:
            return False
        # Trata datetime timezone-aware vs naive
        agora = utc_now()
        data_exp = self.expira_em
        if data_exp.tzinfo is None:
            data_exp = data_exp.replace(tzinfo=timezone.utc)
        return agora > data_exp

class Clique(Base):
    __tablename__ = "cliques"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)
    acessado_em = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    ip = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)

    # Relacionamento reverso
    link = relationship("Link", back_populates="cliques")

    __table_args__ = (
        Index("idx_cliques_link_data", "link_id", "acessado_em"),
    )
