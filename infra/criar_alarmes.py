import boto3
import json

REGIAO = "sa-east-1"
cloudwatch = boto3.client("cloudwatch", region_name=REGIAO)

with open("infra/config_projeto.json") as f:
    config = json.load(f)

TOPIC_ARN = "arn:aws:sns:sa-east-1:557864981139:alertas-triagem-suporte"  # cola o ARN do Passo 2

FUNCOES = ["triagem-ingestao", "triagem-consulta"]

print("Criando alarmes CloudWatch...\n")

for funcao in FUNCOES:
    # ── Alarme de erro ──
    cloudwatch.put_metric_alarm(
        AlarmName=f"alarme-erro-{funcao}",
        AlarmDescription=f"Dispara quando {funcao} tem qualquer erro em 5 minutos",
        Namespace="AWS/Lambda",
        MetricName="Errors",
        Dimensions=[{"Name": "FunctionName", "Value": funcao}],
        Statistic="Sum",
        Period=300,
        EvaluationPeriods=1,
        Threshold=0,
        ComparisonOperator="GreaterThanThreshold",
        AlarmActions=[TOPIC_ARN],
        TreatMissingData="notBreaching",
        Tags=[{"Key": "Projeto", "Value": "triagem-suporte"}]
    )
    print(f"✅ Alarme de erro criado para {funcao}")

    # ── Alarme de duração (perto do timeout de 30s) ──
    cloudwatch.put_metric_alarm(
        AlarmName=f"alarme-duracao-{funcao}",
        AlarmDescription=f"Dispara quando {funcao} demora mais de 20s (perto do timeout)",
        Namespace="AWS/Lambda",
        MetricName="Duration",
        Dimensions=[{"Name": "FunctionName", "Value": funcao}],
        Statistic="Maximum",
        Period=300,
        EvaluationPeriods=1,
        Threshold=20000,  # 20 segundos em milissegundos
        ComparisonOperator="GreaterThanThreshold",
        AlarmActions=[TOPIC_ARN],
        TreatMissingData="notBreaching",
        Tags=[{"Key": "Projeto", "Value": "triagem-suporte"}]
    )
    print(f"✅ Alarme de duração criado para {funcao}")

print("\nAlarmes configurados ✅")