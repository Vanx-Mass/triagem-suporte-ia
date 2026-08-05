import json
import os
import sys
from pathlib import Path

import boto3

print("Verificando ambiente para o projeto de triagem...\n")

erros = []

# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Caminho do arquivo de configuração
CONFIG_FILE = BASE_DIR / "infra" / "config_projeto.json"

# ── config_projeto.json ──
try:
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        config = json.load(f)

    print("✅ config_projeto.json carregado")
    print(f"   Bucket: {config['bucket']}")
    print(f"   Role: {config['role_name']}")

except FileNotFoundError:
    erros.append("config_projeto.json não encontrado — rode criar_role_lambdas.py")
    print("❌ config_projeto.json não encontrado")
    config = {}

# ── Chave da Anthropic API ──
if os.environ.get("ANTHROPIC_API_KEY"):
    print("✅ ANTHROPIC_API_KEY configurada")
else:
    erros.append("ANTHROPIC_API_KEY não encontrada")
    print("❌ ANTHROPIC_API_KEY não encontrada")

# ── S3 ──
if config.get("bucket"):
    try:
        s3 = boto3.client("s3")
        s3.head_bucket(Bucket=config["bucket"])
        print(f"✅ Bucket '{config['bucket']}' existe e está acessível")
    except Exception as e:
        erros.append(f"Bucket não acessível: {e}")
        print(f"❌ Bucket não acessível: {e}")

# ── Budget ──
try:
    budgets = boto3.client("budgets", region_name="us-east-1")
    conta = boto3.client("sts").get_caller_identity()["Account"]

    lista = budgets.describe_budgets(AccountId=conta)["Budgets"]

    if lista:
        print(f"✅ {len(lista)} budget(s) configurado(s)")
    else:
        erros.append("Nenhum budget configurado")
        print("❌ Nenhum budget configurado")

except Exception as e:
    print(f"⚠️ Erro ao verificar budget: {e}")

print()

# ── Verificação de recursos "always-on" ──
try:
    rds = boto3.client("rds", region_name="sa-east-1")

    bancos = rds.describe_db_instances()["DBInstances"]

    ativos = [
        banco["DBInstanceIdentifier"]
        for banco in bancos
        if banco["DBInstanceStatus"] == "available"
    ]

    if ativos:
        print(f"⚠️ RDS ativo encontrado: {ativos} — considere deletar se não for usar")
    else:
        print("✅ Nenhum RDS ativo")

except Exception as e:
    print(f"⚠️ Erro ao verificar RDS: {e}")

try:
    ec2 = boto3.client("ec2", region_name="sa-east-1")

    reservas = ec2.describe_instances(
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": ["running"],
            }
        ]
    )["Reservations"]

    quantidade = sum(len(r["Instances"]) for r in reservas)

    if quantidade:
        print(f"⚠️ {quantidade} instância(s) EC2 rodando — verifique se são necessárias")
    else:
        print("✅ Nenhum EC2 rodando")

except Exception as e:
    print(f"⚠️ Erro ao verificar EC2: {e}")

print()

if erros:
    print("⚠️ Resolva antes de continuar:")
    for erro in erros:
        print(f"   • {erro}")
    sys.exit(1)

print("Ambiente pronto. ✅")