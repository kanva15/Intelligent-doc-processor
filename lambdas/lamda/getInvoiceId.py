import json
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'Invoices'

def lambda_handler(event, context):
    document_id = event['pathParameters']['documentId']
    
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'DocumentId': document_id})
    
    if 'Item' in response:
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item']),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Invoice not found'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
