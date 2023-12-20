from troposphere import (
    Template,
    Parameter,
    GetAtt,
    Output,
)

from troposphere.awslambda import Function, Code, Permission
from troposphere.iam import Role, Policy

# CloudFormation-шаблон
t = Template()

image_uri = t.add_parameter(
    Parameter(
        "ImageURI",
        Description="Image URI for Lambda Function",
        Type="String",
    )
)

telegram_api_key_param = t.add_parameter(
    Parameter(
        "TelegramApiKeyParam",
        Description="Telegram API Key",
        Type="String",
    )
)

execution_role = t.add_resource(
    Role(
        title="LambdaExecutionRole",
        AssumeRolePolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        },
        Policies=[
            Policy(
                title="LambdaExecutionPolicy",
                PolicyName="LambdaExecutionPolicy",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "logs:PutLogEvents",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                            ],
                            "Resource": "arn:aws:logs:*:*:*",
                        },
                    ],
                },
            )
        ],
    )
)

lambda_fn = t.add_resource(
    Function(
        "LambdaFunction",
        PackageType="Image",
        Code=Code(
            ImageUri=image_uri.ref(),
        ),
        Environment={
            "Variables": {
                "TELEGRAM_API_KEY": telegram_api_key_param.ref(),
            },
        },
        Role=GetAtt(execution_role, "Arn"),
    )
)

t.add_resource(
    Permission(
        title="LambdaPermission",
        Action="lambda:InvokeFunction",
        FunctionUrlAuthType="NONE",
        FunctionName=lambda_fn.ref(),
        Principal="*",
    )
)

t.add_output(
    Output(
        "LambdaFunctionUrl",
        Description="Lambda Function URL",
        Value=GetAtt(lambda_fn, "FunctionUrl"),
    )
)

with open("telegram-bot-template.json", "w") as f:
    f.write(t.to_json())
