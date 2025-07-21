import boto3

textract = boto3.client('textract')

def lambda_handler(event, context):
    bucket = event['bucket']
    key = event['key']
    
    response = textract.start_document_analysis(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        FeatureTypes=['FORMS']
    )
    
    return {
        'jobId': response['JobId'],
        'bucket': bucket,
        'key': key
    }
