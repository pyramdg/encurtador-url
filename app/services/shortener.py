import string
import secrets
from sqlalchemy.orm import Session
from app.models import Link
from app.config import settings

# Caracteres Base62 (0-9, a-z, A-Z)
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

def encode_base62(num: int) -> str:
    """Codifica um número inteiro positivo em Base62."""
    if num == 0:
        return BASE62_ALPHABET[0]
    result = []
    base = len(BASE62_ALPHABET)
    while num > 0:
        num, rem = divmod(num, base)
        result.append(BASE62_ALPHABET[rem])
    return "".join(reversed(result))

def generate_random_code(length: int = 6) -> str:
    """Gera uma string aleatória criptograficamente segura de tamanho fixo."""
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))

def get_unique_short_code(db: Session, length: int = 6, max_retries: int = 10) -> str:
    """
    Gera um código único que não colide com nenhum link existente no banco.
    Caso haja colisão improvável, tenta novamente com recálculo ou aumento de comprimento.
    """
    for _ in range(max_retries):
        code = generate_random_code(length)
        exists = db.query(Link).filter(Link.codigo == code).first()
        if not exists:
            return code
    # Se atingir max_retries, incrementa o tamanho para 7 ou 8 caracteres
    return generate_random_code(length + 1)
