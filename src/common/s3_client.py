import boto3
import json
import os
from datetime import datetime

s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "sa-east-1"))
BUCKET = os.environ["S3_BUCKET"]


def salvar_ticket(ticket_id: str, dados: dict) -> str:
    """Salva um ticket como JSON no S3. Retorna a chave usada."""
    chave = f"tickets/{ticket_id}.json"
    corpo = json.dumps(dados, ensure_ascii=False, default=str)
    s3.put_object(
        Bucket=BUCKET,
        Key=chave,
        Body=corpo.encode("utf-8"),
        ContentType="application/json"
    )
    return chave


def ler_ticket(ticket_id: str) -> dict:
    """Lê um ticket específico do S3."""
    chave = f"tickets/{ticket_id}.json"
    resposta = s3.get_object(Bucket=BUCKET, Key=chave)
    return json.loads(resposta["Body"].read())


def listar_tickets() -> list[dict]:
    """Lista todos os tickets salvos no S3."""
    paginador = s3.get_paginator("list_objects_v2")
    tickets = []
    for pagina in paginador.paginate(Bucket=BUCKET, Prefix="tickets/"):
        for obj in pagina.get("Contents", []):
            if obj["Key"] == "tickets/":
                continue
            resposta = s3.get_object(Bucket=BUCKET, Key=obj["Key"])
            tickets.append(json.loads(resposta["Body"].read()))
    return tickets