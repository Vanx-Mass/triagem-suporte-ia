import boto3
import json

REGIAO = "sa-east-1"

apigw = boto3.client("apigatewayv2", region_name=REGIAO)
lambda_client = boto3.client("lambda", region_name=REGIAO)
conta = boto3.client("sts").get_caller_identity()["Account"]

print("Criando API Gateway...\n")

# ── 1. Cria a HTTP API ──
api = apigw.create_api(
    Name="api-triagem-suporte",
    ProtocolType="HTTP",
    CorsConfiguration={
        "AllowOrigins": ["*"],
        "AllowMethods": ["GET", "POST", "PATCH"],
        "AllowHeaders": ["content-type"]
    }
)
api_id = api["ApiId"]
print(f"✅ API criada: {api_id}")

# ── 2. Integrações com as duas Lambdas ──
def criar_integracao(nome_funcao: str) -> str:
    arn_funcao = lambda_client.get_function(FunctionName=nome_funcao)["Configuration"]["FunctionArn"]
    integracao = apigw.create_integration(
        ApiId=api_id,
        IntegrationType="AWS_PROXY",
        IntegrationUri=arn_funcao,
        PayloadFormatVersion="2.0"
    )
    # Permite o API Gateway invocar a Lambda
    try:
        lambda_client.add_permission(
            FunctionName=nome_funcao,
            StatementId=f"apigw-invoke-{nome_funcao}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{REGIAO}:{conta}:{api_id}/*/*"
        )
    except lambda_client.exceptions.ResourceConflictException:
        pass
    return integracao["IntegrationId"]

integracao_ingestao = criar_integracao("triagem-ingestao")
integracao_consulta = criar_integracao("triagem-consulta")
print("✅ Integrações criadas")

# ── 3. Rotas ──
rotas = [
    ("POST /tickets", integracao_ingestao),
    ("GET /tickets", integracao_consulta),
    ("PATCH /tickets/{id}", integracao_consulta),
]

for chave_rota, integracao_id in rotas:
    apigw.create_route(
        ApiId=api_id,
        RouteKey=chave_rota,
        Target=f"integrations/{integracao_id}"
    )
    print(f"✅ Rota criada: {chave_rota}")

# ── 4. Deploy (stage) ──
apigw.create_stage(
    ApiId=api_id,
    StageName="$default",
    AutoDeploy=True
)

url_final = f"https://{api_id}.execute-api.{REGIAO}.amazonaws.com"
print(f"\n🌐 URL da API: {url_final}")

with open("infra/config_projeto.json") as f:
    config = json.load(f)
config["api_url"] = url_final
with open("infra/config_projeto.json", "w") as f:
    json.dump(config, f, indent=2)

print("Salvo em config_projeto.json ✅")