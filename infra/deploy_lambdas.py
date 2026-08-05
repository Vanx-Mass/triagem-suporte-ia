import boto3
import json
import zipfile
import os
import shutil

REGIAO = "sa-east-1"

with open("infra/config_projeto.json") as f:
    config = json.load(f)

ROLE_ARN = config["role_arn"]
BUCKET = config["bucket"]

lambda_client = boto3.client("lambda", region_name=REGIAO)


def empacotar(pasta_origem: str, nome_zip: str):
    """Cria um .zip com o código da Lambda, incluindo dependências instaladas."""
    pasta_build = f"build_{nome_zip}"
    if os.path.exists(pasta_build):
        shutil.rmtree(pasta_build)
    os.makedirs(pasta_build)

    # Copia o código-fonte
    for arquivo in os.listdir(pasta_origem):
        if arquivo.endswith(".py"):
            shutil.copy(os.path.join(pasta_origem, arquivo), pasta_build)

    # Instala as dependências direto na pasta de build
    os.system(
        f"pip install anthropic boto3 -t {pasta_build} "
        f"--platform manylinux2014_x86_64 "
        f"--implementation cp "
        f"--python-version 3.12 "
        f"--only-binary=:all: "
        f"--quiet"
    )

    caminho_zip = f"{nome_zip}.zip"
    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for pasta_raiz, _, arquivos in os.walk(pasta_build):
            for arquivo in arquivos:
                caminho_completo = os.path.join(pasta_raiz, arquivo)
                caminho_relativo = os.path.relpath(caminho_completo, pasta_build)
                zf.write(caminho_completo, caminho_relativo)

    shutil.rmtree(pasta_build)
    return caminho_zip


def criar_ou_atualizar_lambda(nome_funcao: str, caminho_zip: str, handler: str):
    with open(caminho_zip, "rb") as f:
        codigo = f.read()

    variaveis_ambiente = {
        "ANTHROPIC_API_KEY": os.environ["ANTHROPIC_API_KEY"],
        "S3_BUCKET": BUCKET,
    }

    try:
        lambda_client.create_function(
            FunctionName=nome_funcao,
            Runtime="python3.12",
            Role=ROLE_ARN,
            Handler=handler,
            Code={"ZipFile": codigo},
            Timeout=30,
            MemorySize=256,
            Environment={"Variables": variaveis_ambiente},
            Tags={"Projeto": "triagem-suporte"},
        )
        print(f"✅ Lambda {nome_funcao} criada")
    except lambda_client.exceptions.ResourceConflictException:
        # Atualiza o código
        lambda_client.update_function_code(FunctionName=nome_funcao, ZipFile=codigo)

        # Aguarda a atualização do código terminar
        waiter = lambda_client.get_waiter("function_updated")
        waiter.wait(FunctionName=nome_funcao)

        # Atualiza a configuração (variáveis de ambiente)
        lambda_client.update_function_configuration(
            FunctionName=nome_funcao,
            Environment={"Variables": variaveis_ambiente},
        )

        # Aguarda a atualização da configuração terminar
        waiter.wait(FunctionName=nome_funcao)

        print(f"✅ Lambda {nome_funcao} atualizada (já existia)")


if __name__ == "__main__":
    print("Empacotando Lambda de ingestão...")
    zip_ingestao = empacotar("src/ingestao", "ingestao")

    # s3_client.py é compartilhado — copia pra dentro do zip também
    with zipfile.ZipFile(zip_ingestao, "a") as zf:
        zf.write("src/common/s3_client.py", "s3_client.py")

    criar_ou_atualizar_lambda(
        nome_funcao="triagem-ingestao",
        caminho_zip=zip_ingestao,
        handler="handler.lambda_handler",
    )
    os.remove(zip_ingestao)

    print("\nEmpacotando Lambda de consulta...")
    zip_consulta = empacotar("src/consulta", "consulta")

    with zipfile.ZipFile(zip_consulta, "a") as zf:
        zf.write("src/common/s3_client.py", "s3_client.py")

    criar_ou_atualizar_lambda(
        nome_funcao="triagem-consulta",
        caminho_zip=zip_consulta,
        handler="handler.lambda_handler",
    )
    os.remove(zip_consulta)

    print("\nDeploy concluído ✅")