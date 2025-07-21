import json
import boto3

sfn = boto3.client('stepfunctions')

STEP_FUNCTION_ARN = 'arn:aws:states:us-east-1:354918408805:stateMachine:DocumentProcessingWorkflow'

def lambda_handler(event, context):
    print("Event:", json.dumps(event))

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    input_payload = {
        "bucket": bucket,
        "key": key
    }

    response = sfn.start_execution(
        stateMachineArn=STEP_FUNCTION_ARN,
        input=json.dumps(input_payload)
    )

    return {
        'statusCode': 200,
        'body': f"Step Function triggered: {response['executionArn']}"
    }