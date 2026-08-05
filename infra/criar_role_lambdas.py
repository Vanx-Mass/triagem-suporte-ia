import boto3
import json

iam = boto3.client("iam")

ROLE_NAME = "role-lambda-triagem-suporte"
POLICY_NAME = "policy-lambda-triagem-suporte"
BUCKET = "triagem-suporte-ivan"

print("Criando IAM Role para as Lambdas...\n")

trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "lambda.amazonaws.com"},
        "Action": "sts:AssumeRole"
    }]
}

try:
    iam.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Role para as Lambdas do sistema de triagem"
    )
    print(f"✅ Role criada: {ROLE_NAME}")
except iam.exceptions.EntityAlreadyExistsException:
    print(f"⚠️  Role {ROLE_NAME} já existe — continuando")

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3Acesso",
            "Effect": "Allow",
            "Action": ["s3:PutObject", "s3:GetObject", "s3:ListBucket"],
            "Resource": [f"arn:aws:s3:::{BUCKET}", f"arn:aws:s3:::{BUCKET}/*"]
        },
        {
            "Sid": "CloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}

try:
    policy = iam.create_policy(
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy_document)
    )
    policy_arn = policy["Policy"]["Arn"]
    print(f"✅ Policy criada: {POLICY_NAME}")
except iam.exceptions.EntityAlreadyExistsException:
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    policy_arn = f"arn:aws:iam::{account_id}:policy/{POLICY_NAME}"
    print(f"⚠️  Policy {POLICY_NAME} já existe — continuando")

try:
    iam.attach_role_policy(RoleName=ROLE_NAME, PolicyArn=policy_arn)
    print(f"✅ Policy anexada à role")
except Exception as e:
    if "already attached" not in str(e).lower():
        raise
    print("⚠️  Policy já estava anexada")

role_arn = iam.get_role(RoleName=ROLE_NAME)["Role"]["Arn"]

with open("config_projeto.json", "w") as f:
    json.dump({
        "bucket": BUCKET,
        "role_arn": role_arn,
        "role_name": ROLE_NAME
    }, f, indent=2)

print(f"\nRole ARN: {role_arn}")
print("Salvo em config_projeto.json ✅")