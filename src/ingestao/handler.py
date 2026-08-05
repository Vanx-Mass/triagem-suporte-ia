import json
import uuid
from datetime import datetime

from classificador import classificar_ticket
from s3_client import salvar_ticket


def lambda_handler(event, context):
    print(f"Body bruto recebido: {event.get('body')!r}")
    print(f"isBase64Encoded: {event.get('isBase64Encoded')}")

    try:
        corpo = json.loads(event.get("body", "{}"))
        texto = corpo.get("texto", "").strip()

        if not texto:
            return _responder(400, {"erro": "Campo 'texto' é obrigatório"})

        ticket_id = str(uuid.uuid4())[:8]
        classificacao = classificar_ticket(texto)

        ticket = {
            "id": ticket_id,
            "texto_bruto": texto,
            "categoria": classificacao["categoria"],
            "urgencia": classificacao["urgencia"],
            "status": "pendente_revisao",
            "criado_em": datetime.utcnow().isoformat()
        }

        salvar_ticket(ticket_id, ticket)

        return _responder(201, ticket)

    except Exception as e:
        print(f"Erro ao processar ticket: {e}")
        return _responder(500, {"erro": "Erro interno ao processar ticket"})


def _responder(status: int, corpo: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(corpo, ensure_ascii=False)
    }