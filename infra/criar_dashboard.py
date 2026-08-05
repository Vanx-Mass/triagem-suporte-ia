import boto3
import json

REGIAO = "sa-east-1"
cloudwatch = boto3.client("cloudwatch", region_name=REGIAO)

corpo_dashboard = {
    "widgets": [
        {
            "type": "metric",
            "x": 0, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "Invocações por Lambda",
                "metrics": [
                    ["AWS/Lambda", "Invocations", "FunctionName", "triagem-ingestao"],
                    ["AWS/Lambda", "Invocations", "FunctionName", "triagem-consulta"]
                ],
                "period": 300,
                "stat": "Sum",
                "region": REGIAO
            }
        },
        {
            "type": "metric",
            "x": 12, "y": 0, "width": 12, "height": 6,
            "properties": {
                "title": "Erros por Lambda",
                "metrics": [
                    ["AWS/Lambda", "Errors", "FunctionName", "triagem-ingestao"],
                    ["AWS/Lambda", "Errors", "FunctionName", "triagem-consulta"]
                ],
                "period": 300,
                "stat": "Sum",
                "region": REGIAO
            }
        },
        {
            "type": "metric",
            "x": 0, "y": 6, "width": 12, "height": 6,
            "properties": {
                "title": "Duração (ms)",
                "metrics": [
                    ["AWS/Lambda", "Duration", "FunctionName", "triagem-ingestao"],
                    ["AWS/Lambda", "Duration", "FunctionName", "triagem-consulta"]
                ],
                "period": 300,
                "stat": "Average",
                "region": REGIAO
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName="triagem-suporte",
    DashboardBody=json.dumps(corpo_dashboard)
)

print("✅ Dashboard criado")
print(f"🌐 Veja em: https://{REGIAO}.console.aws.amazon.com/cloudwatch/home?region={REGIAO}#dashboards:name=triagem-suporte")