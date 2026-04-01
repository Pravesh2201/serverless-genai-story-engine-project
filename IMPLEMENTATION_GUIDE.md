# Implementation Guide — Serverless AI Story Generation System

This guide walks through every step to recreate this project from scratch in your own AWS account.

---

## Prerequisites

- An active AWS account
- AWS Console access
- Basic understanding of Python
- Amazon Q Developer enabled in your IDE or AWS Console (optional but recommended)

---

## Step 1 — Enable Amazon Bedrock: Nova Pro Model

Amazon Bedrock hosts the Nova Pro foundation model that generates the stories.

1. Go to **AWS Console → Amazon Bedrock → Model catalog**
2. Search for **Nova Pro** (by Amazon)
3. If not already enabled, click **Request model access** and submit use case details
   - Note: Anthropic models require first-time customers to submit use case details before invoking
4. Wait for access to be approved (usually instant for Nova Pro)
5. Confirm the model shows as **Serverless** — no provisioned throughput needed

**Model used:** `amazon.nova-pro-v1:0`

---

## Step 2 — Create the S3 Bucket

The S3 bucket stores each generated story as a `.txt` file.

1. Go to **AWS Console → Amazon S3 → Buckets**
2. Click **Create bucket**
3. Set bucket name: `story-bucket-<your-unique-id>` (e.g. `story-bucket-cb599c80`)
4. Choose your preferred AWS region
5. Leave all other settings as default (Block Public Access: ON)
6. Click **Create bucket**

The Lambda function will write files to this bucket automatically. No manual uploads needed.

---

## Step 3 — Create the DynamoDB Table

The DynamoDB table stores metadata about each generated story.

1. Go to **AWS Console → Amazon DynamoDB → Tables**
2. Click **Create table**
3. Set table name: `story-table-<your-unique-id>` (e.g. `story-table-cb599c80`)
4. Set partition key: `uid` with type **String (S)**
5. Leave sort key empty
6. Leave index count as 0
7. Keep **Provisioned** capacity mode (default)
8. Deletion protection: **Off**
9. Click **Create table**

Wait for the table status to show **Active** (green checkmark) before proceeding.

---

## Step 4 — Create the Lambda Function

The Lambda function is the brain — it calls Bedrock, saves to S3, and writes to DynamoDB.

1. Go to **AWS Console → AWS Lambda → Functions**
2. Click **Create function**
3. Choose **Author from scratch**
4. Set function name: `story-teller-<your-unique-id>` (e.g. `story-teller-cb599c80`)
5. Runtime: **Python 3.13**
6. Package type: **Zip**
7. Architecture: **x86_64** (default)
8. Click **Create function**

### Configure General Settings

Go to **Configuration → General configuration → Edit:**

- Memory: `128 MB`
- Timeout: `0 min 15 sec`
- Ephemeral storage: `512 MB`
- SnapStart: `None`

Click **Save**.

---

## Step 5 — Add Environment Variables

The Lambda function reads the S3 bucket name and DynamoDB table name from environment variables — this avoids hardcoding resource names in code.

1. Inside your Lambda function, go to **Configuration → Environment variables**
2. Click **Edit → Add environment variable**
3. Add the following two variables:

| Key | Value |
|---|---|
| `BUCKET_NAME` | `story-bucket-<your-unique-id>` |
| `TABLE_NAME` | `story-table-<your-unique-id>` |

4. Click **Save**

---

## Step 6 — Write the Lambda Code (with Amazon Q Developer)

This is where Amazon Q Developer helps you write the code using inline comment-driven suggestions.

1. Inside your Lambda function, click the **Code** tab
2. Open `lambda_function.py`
3. Add the following imports at the top:

```python
import boto3
import json
import hashlib
import os
```

4. Write instructional comments describing what each section should do. Amazon Q Developer reads these comments and suggests the code to complete the task. For example:

```python
# Get environment variables for S3 bucket name and DynamoDB table name

# Create boto3 clients for Bedrock runtime, S3, and DynamoDB

# Define the prompt to send to Bedrock asking it to write a children's story

# Invoke the Bedrock Nova Pro model with the prompt and extract the story text

# Generate a unique ID for this story using hashlib

# Save the story text as a .txt file to the S3 bucket

# Write the story metadata (uid, title, s3 key, timestamp) to DynamoDB

# Return a 200 status code response
```

5. After each comment, press **Enter** and wait for Amazon Q to suggest the code
6. Press **Tab** to accept a suggestion, or keep typing to write your own
7. Repeat for each section until the function is complete

### Final Lambda Function Structure

```python
import boto3
import json
import hashlib
import os

def lambda_handler(event, context):

    # Environment variables
    bucket_name = os.environ['BUCKET_NAME']
    table_name  = os.environ['TABLE_NAME']

    # AWS clients
    bedrock  = boto3.client('bedrock-runtime')
    s3       = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table    = dynamodb.Table(table_name)

    # Prompt for Bedrock
    prompt = "Write a short children's story."

    # Invoke Bedrock Nova Pro
    response = bedrock.invoke_model(
        modelId='amazon.nova-pro-v1:0',
        body=json.dumps({
            "messages": [{"role": "user", "content": prompt}]
        }),
        contentType='application/json',
        accept='application/json'
    )

    result      = json.loads(response['body'].read())
    story_text  = result['output']['message']['content'][0]['text']

    # Generate unique ID
    uid = hashlib.md5(story_text.encode()).hexdigest()[:10]

    # Save story to S3
    s3_key = f"{uid}.txt"
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=json.dumps({"story": story_text})
    )

    # Write metadata to DynamoDB
    table.put_item(Item={
        'uid':   uid,
        's3key': s3_key,
        'bucket': bucket_name
    })

    return {'statusCode': 200, 'body': ''}
```

8. Click **Deploy** to save and deploy the function

---

## Step 7 — Set Lambda Permissions (IAM Role)

The Lambda execution role needs permissions to call Bedrock, S3, and DynamoDB.

1. Go to **Configuration → Permissions**
2. Click on the execution role link (opens IAM)
3. Click **Add permissions → Attach policies**
4. Attach the following managed policies:
   - `AmazonBedrockFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonDynamoDBFullAccess`
5. Click **Add permissions**

> For production use, replace these with least-privilege custom policies.

---

## Step 8 — Test the Function

1. Inside your Lambda function, click the **Test** tab
2. Click **Create new test event**
3. Event name: `test`
4. Leave the event JSON as the default `{}` empty object
5. Click **Save**
6. Click **Test**

### Expected Result

```json
{
  "statusCode": 200,
  "body": ""
}
```

The execution log will show the generated story text in JSON format. A status of **Succeeded** confirms everything worked.

---

## Step 9 — Verify the Story in S3

1. Go to **AWS Console → Amazon S3 → story-bucket-<your-id>**
2. You should see a new `.txt` file named with a unique hash ID (e.g. `1d4d8ef8e4.txt`)
3. Click the file → **Open** to read the generated story
4. The file contains JSON with the story text:

```json
{
  "story": "In a quaint little town, there lived two cats named Whiskers and Shadow..."
}
```

---

## Step 10 — Verify Metadata in DynamoDB (Optional Enhancement)

If you added the DynamoDB write step:

1. Go to **AWS Console → Amazon DynamoDB → Tables**
2. Select `story-table-<your-id>`
3. Click **Actions → Explore items**
4. Click **Run** (Scan mode)
5. Items returned should show your story's `uid`, `s3key`, and `bucket` fields

> Note: If 0 items are returned, the DynamoDB write step may need to be added using Amazon Q Developer inline suggestions (Step 11 in the original CloudQuest flow).

---

## Step 11 — Enhance with DynamoDB Metadata Writing

To add full metadata writing using Amazon Q Developer:

1. In the Lambda code editor, add a comment after the S3 write:

```python
# Write story metadata including uid, title, s3 key, and timestamp to DynamoDB table
```

2. Accept Amazon Q's suggestion or write the `table.put_item()` call manually
3. Deploy the updated function
4. Run the test again and verify the item appears in DynamoDB

---

## Architecture Summary

```
Invoke Lambda
     │
     ▼
Bedrock Nova Pro ──► generates story text
     │
     ▼
Generate unique hash ID (hashlib.md5)
     │
     ├──► S3: save story as {uid}.txt
     │
     └──► DynamoDB: write {uid, s3key, bucket} metadata
     │
     ▼
Return 200 OK
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `AccessDeniedException` from Bedrock | Attach `AmazonBedrockFullAccess` to Lambda IAM role |
| Story not appearing in S3 | Check `BUCKET_NAME` env variable matches actual bucket name |
| DynamoDB items returning 0 | Confirm `TABLE_NAME` env variable is correct and `put_item` code is deployed |
| Lambda timeout | Increase timeout to 30–60 seconds if Bedrock response is slow |
| `NoRegionError` | Ensure Lambda is deployed in the same region as S3 and DynamoDB |

---

## Cost Estimate (Approximate)

| Service | Free Tier | Estimated Cost |
|---|---|---|
| AWS Lambda | 1M requests/month free | ~$0 for testing |
| Amazon Bedrock Nova Pro | Pay per token | ~$0.001 per story |
| Amazon S3 | 5 GB free | ~$0 for small files |
| Amazon DynamoDB | 25 GB free | ~$0 for low volume |

This project runs almost entirely within AWS Free Tier for personal testing.

---

## Author

Built as a hands-on cloud project exploring serverless architecture, generative AI integration on Amazon Bedrock, and AI-assisted development using Amazon Q Developer.
