from fastapi import APIRouter, Request, Header, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.database import get_db
from app.middleware.rate_limit import limiter
from app.models.deposit import DepositProvider
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.post("/mpesa")
@limiter.limit("30/minute")
async def mpesa_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str | None = Header(default=None),
):
    """
    Endpoint que a Vodacom M-Pesa vai chamar para confirmar um pagamento.
    Ainda sem credenciais reais — este endpoint já está pronto para receber
    o callback assim que a integração real for ligada (ver services/payment_providers/mpesa.py).
    """
    raw_body = await request.body()
    body_json = await request.json()

    # O nome exato do campo de referência varia por provedor — ajustar quando
    # tivermos a documentação oficial da API M-Pesa Moçambique.
    external_reference = body_json.get("reference") or body_json.get("input_ThirdPartyReference", "")
    if not external_reference:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Referência ausente no callback")

    service = WebhookService(db)
    callback = service.handle_callback(
        provider=DepositProvider.MPESA,
        raw_body=raw_body,
        signature=x_signature,
        ip_address=request.client.host if request.client else None,
        external_reference=external_reference,
    )
    return {"received": True, "processed": callback.processed}


@router.post("/emola")
@limiter.limit("30/minute")
async def emola_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: str | None = Header(default=None),
):
    """Endpoint que a Movitel e-Mola vai chamar para confirmar um pagamento (mesma lógica, provedor independente)."""
    raw_body = await request.body()
    body_json = await request.json()

    external_reference = body_json.get("reference", "")
    if not external_reference:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Referência ausente no callback")

    service = WebhookService(db)
    callback = service.handle_callback(
        provider=DepositProvider.EMOLA,
        raw_body=raw_body,
        signature=x_signature,
        ip_address=request.client.host if request.client else None,
        external_reference=external_reference,
    )
    return {"received": True, "processed": callback.processed}
