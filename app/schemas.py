from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List, Dict
from datetime import datetime
import re

class LinkCreate(BaseModel):
    url: str
    dias_validade: Optional[int] = None
    expira_em: Optional[datetime] = None
    custom_alias: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validar_url(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$", v):
            raise ValueError("URL inválida. O link deve começar com http:// ou https:// e possuir domínio válido.")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validar_custom_alias(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not re.match(r"^[a-zA-Z0-9_-]{3,30}$", v):
            raise ValueError("O alias personalizado deve conter entre 3 e 30 caracteres alfanuméricos, hífen ou underline.")
        return v

class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    url_original: str
    url_curta: str
    criado_em: datetime
    expira_em: Optional[datetime]
    ativo: bool

class CliqueDetalhe(BaseModel):
    acessado_em: datetime
    ip: Optional[str]
    user_agent: Optional[str]
    referer: Optional[str]
    dispositivo: Optional[str] = None
    navegador: Optional[str] = None

class StatsResponse(BaseModel):
    codigo: str
    url_original: str
    url_curta: str
    criado_em: datetime
    expira_em: Optional[datetime]
    ativo: bool
    expirado: bool
    total_cliques: int
    cliques_por_dia: Dict[str, int]
    cliques_por_dispositivo: Dict[str, int]
    cliques_por_navegador: Dict[str, int]
    ultimos_cliques: List[CliqueDetalhe]
