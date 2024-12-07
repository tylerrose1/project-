import boto3
import json

# Initialize AWS Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-2')  # Replace 'your-region'

def test_lambda():
    payload = {"festival_name": "Sundance Film Festival"}

    try:
        response = lambda_client.invoke(
            FunctionName="predict_recommendations",  # Replace with your Lambda function name
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )
        response_payload = json.loads(response['Payload'].read())
        print("Lambda Response:", response_payload)
    except Exception as e:
        print("Error invoking Lambda:", str(e))

if __name__ == "__main__":
    test_lambda()