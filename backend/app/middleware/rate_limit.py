from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Em Docker/VM normal, a memória do processo já chega (um único processo,
# sempre vivo). Em serverless (Vercel), cada invocação pode ser uma
# instância isolada — sem REDIS_URL definido, o limite deixa de ser fiável
# nesse ambiente. Configura REDIS_URL (ex.: Upstash, grátis) antes de ligar
# credenciais reais de M-Pesa/e-Mola/Binance em produção na Vercel.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL if settings.REDIS_URL else None,
)

