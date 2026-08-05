import boto3

REGIAO = "sa-east-1"
TAGS = {"Projeto": "triagem-suporte", "Ambiente": "portfolio"}

lambda_client = boto3.client("lambda", region_name=REGIAO)
s3 = boto3.client("s3", region_name=REGIAO)

with open("infra/config_projeto.json") as f:
    import json
    config = json.load(f)

print("Aplicando tags de custo...\n")

# ── Lambdas ──
for funcao in ["triagem-ingestao", "triagem-consulta"]:
    arn = lambda_client.get_function(FunctionName=funcao)["Configuration"]["FunctionArn"]
    lambda_client.tag_resource(Resource=arn, Tags=TAGS)
    print(f"✅ Tags aplicadas em {funcao}")

# ── S3 bucket ──
s3.put_bucket_tagging(
    Bucket=config["bucket"],
    Tagging={"TagSet": [{"Key": k, "Value": v} for k, v in TAGS.items()]}
)
print(f"✅ Tags aplicadas no bucket {config['bucket']}")

print("\n⚠️  Tags novas podem levar até 24h para aparecer no Cost Explorer.")
print("Tags configuradas ✅")