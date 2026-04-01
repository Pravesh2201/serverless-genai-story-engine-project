import boto3
import json
import os
import random
import string

def lambda_handler(event, context):

    # Initialize AWS clients
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1"
    )
    s3 = boto3.client('s3')
    dynamodb = boto3.client('dynamodb')

    # Environment variables
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    TABLE_NAME = os.environ.get("TABLE_NAME")

    # Model ID
    MODEL_ID = "amazon.nova-pro-v1:0"

    # Prompt
    user_message = """Write a short story about a cat named Tom and a dog named Jerry.
The story should be about friendship and fun, under 100 words.
Return output strictly in JSON format like:
{"title": "Story Title", "story": "Story content"}
"""

    # Request payload
    request_payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": user_message}]
            }
        ],
        "inferenceConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "maxTokens": 512
        }
    }

    try:
        # Invoke Bedrock model
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_payload)
        )

        # Parse response
        response_body = json.loads(response['body'].read())
        generated_text = response_body['output']['message']['content'][0]['text']

        # Safe JSON parsing
        try:
            story_json = json.loads(generated_text)
            title = story_json.get("title", "Untitled")
            story = story_json.get("story", generated_text)
        except Exception:
            title = "Tom and Jerry Story"
            story = generated_text

        # Generate unique ID
        uid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

        # Upload story to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{uid}.txt",
            Body=story
        )

        # Store metadata in DynamoDB
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                'title': {'S': title},
                'uid': {'S': uid},
                'bucket': {'S': BUCKET_NAME}
            }
        )

        # FINAL REQUIRED RESPONSE
        return {
            'statusCode': 200,
            'body': f"Story saved to {uid}.txt"  # ✅ Fixed: now includes the actual filename
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
