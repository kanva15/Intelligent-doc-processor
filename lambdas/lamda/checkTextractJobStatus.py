import boto3

textract = boto3.client('textract')

def lambda_handler(event, context):
    job_id = event['jobId']
    
    response = textract.get_document_analysis(JobId=job_id)
    status = response['JobStatus']
    
    return {
        "status": status,
        "jobId": job_id,
        "bucket": event['bucket'],
        "key": event['key']
    }
