import json
from datetime import datetime

from s3_client import listar_tickets, ler_ticket, salvar_ticket


def lambda_handler(event, context):
    metodo = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    print(f"Método recebido: {metodo}")
    print(f"pathParameters: {event.get('pathParameters')}")
    print(f"Body bruto recebido: {event.get('body')!r}")

    try:
        if metodo == "GET":
            return _listar()

        if metodo == "PATCH":
            ticket_id = event.get("pathParameters", {}).get("id")
            return _marcar_revisado(ticket_id)

        return _responder(405, {"erro": "Método não suportado"})

    except Exception as e:
        print(f"Erro na consulta: {e}")
        return _responder(500, {"erro": "Erro interno ao consultar tickets"})


def _listar() -> dict:
    tickets = listar_tickets()
    tickets.sort(key=lambda t: t.get("criado_em", ""), reverse=True)
    return _responder(200, {"tickets": tickets, "total": len(tickets)})


def _marcar_revisado(ticket_id: str) -> dict:
    if not ticket_id:
        return _responder(400, {"erro": "ID do ticket é obrigatório"})

    ticket = ler_ticket(ticket_id)
    ticket["status"] = "revisado"
    ticket["revisado_em"] = datetime.utcnow().isoformat()
    salvar_ticket(ticket_id, ticket)

    return _responder(200, ticket)


def _responder(status: int, corpo: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(corpo, ensure_ascii=False)
    }