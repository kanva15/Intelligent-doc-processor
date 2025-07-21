import boto3
import json

textract = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Replace with your DynamoDB table name and SNS topic ARN
TABLE_NAME = 'Invoices'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:354918408805:InvoiceProcessingSuccess'

def lambda_handler(event, context):
    job_id = event['jobId']
    bucket = event['bucket']
    key = event['key']
    
    # Get Textract result
    response = textract.get_document_analysis(JobId=job_id)
    blocks = response['Blocks']
    
    extracted_data = {}
    
    for block in blocks:
        if block['BlockType'] == 'KEY_VALUE_SET' and 'EntityTypes' in block and 'KEY' in block['EntityTypes']:
            key_name = None
            value_text = None
            
            for relationship in block.get('Relationships', []):
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        for b in blocks:
                            if b['Id'] == child_id and b['BlockType'] == 'WORD':
                                key_name = b['Text'] if not key_name else key_name + ' ' + b['Text']
            
            # Find the VALUE block
            for rel in block.get('Relationships', []):
                if rel['Type'] == 'VALUE':
                    for value_id in rel['Ids']:
                        for b in blocks:
                            if b['Id'] == value_id:
                                for subrel in b.get('Relationships', []):
                                    if subrel['Type'] == 'CHILD':
                                        for cid in subrel['Ids']:
                                            for bb in blocks:
                                                if bb['Id'] == cid and bb['BlockType'] == 'WORD':
                                                    value_text = bb['Text'] if not value_text else value_text + ' ' + bb['Text']
            
            if key_name and value_text:
                extracted_data[key_name.strip()] = value_text.strip()
    
    # Write to DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item={
        'DocumentId': job_id,
        'S3Bucket': bucket,
        'S3Key': key,
        'ExtractedFields': extracted_data
    })
    
    # Send SNS notification
    message = {
        'DocumentId': job_id,
        'Bucket': bucket,
        'Key': key,
        'ExtractedFields': extracted_data,
        'Status': 'SUCCESS',
        'Note': 'Invoice processed and saved to DynamoDB.'
    }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message, indent=2),
        Subject='Invoice Processed Successfully'
    )

    return {
        'statusCode': 200,
        'message': 'Data saved to DynamoDB and notification sent.'
    }
