# Serverless AI Story Generation System

An end-to-end serverless application on AWS that uses Generative AI to automatically generate children's stories, store them in Amazon S3, and track metadata in Amazon DynamoDB — all orchestrated by a single AWS Lambda function written with the help of Amazon Q Developer.

---

## Live Output Example

The system generated this story on its first successful test run:

> *"In a quaint little town, there lived two cats named Whiskers and Shadow. Whiskers was a fluffy, orange tabby with a curious nature, while Shadow was a sleek, black feline with a mysterious aura. They lived in neighboring houses but often met at the local park. One sunny afternoon, Whiskers discovered a hidden garden behind the park. Excited, he raced to tell Shadow. Together, they explored the garden, finding a sparkling pond and colorful flowers. As they played, they met Luna, a wise old cat who lived in the garden. Luna shared stories of the garden's magic, and the trio became fast friends. They spent their days exploring, learning, and having adventures. Whiskers and Shadow's friendship grew stronger, and they became known as the park's adventurous duo. Their tales of magic and friendship spread throughout the town, inspiring other cats to seek out their own adventures."*

Stored as `1d4d8ef8e4.txt` in S3 — 902 bytes, generated and saved automatically.

---

## Architecture

```
Developer
   │
   ├──► Amazon Q Developer  (AI-assisted code suggestions)
   │         │
   │         ▼
   └──► AWS Lambda: story-teller-cb599c80  (Python 3.13)
              │
              ├──► Amazon Bedrock: Nova Pro  (story generation)
              │
              ├──► Amazon S3: story-bucket-cb599c80  (stores .txt story file)
              │
              └──► Amazon DynamoDB: story-table-cb599c80  (stores metadata)
```

---

## Tech Stack

| Service | Role | Details |
|---|---|---|
| **AWS Lambda** | Orchestrator | Python 3.13, 128 MB memory, 15s timeout |
| **Amazon Bedrock** | AI story generation | Nova Pro foundation model (Serverless) |
| **Amazon Q Developer** | AI coding assistant | Inline code suggestions inside Lambda editor |
| **Amazon S3** | Story storage | Stores generated story as `.txt` file |
| **Amazon DynamoDB** | Metadata storage | Partition key: `uid (S)` |

---

## Project Structure

```
story-teller-cb599c80/
│
├── lambda_function.py        # Main Lambda handler (Python 3.13)
│
├── README.md                 # Project overview (this file)
│
└── IMPLEMENTATION_GUIDE.md   # Step-by-step setup guide
```

---

## Environment Variables

The Lambda function uses two environment variables configured in the AWS Console:

| Key | Value |
|---|---|
| `BUCKET_NAME` | `story-bucket-cb599c80` |
| `TABLE_NAME` | `story-table-cb599c80` |

---

## Key Features

- **Zero infrastructure management** — fully serverless, no servers to provision
- **AI-powered content** — Amazon Bedrock Nova Pro generates unique stories on every invocation
- **AI-assisted development** — Amazon Q Developer wrote inline code suggestions inside the Lambda editor
- **Automatic storage** — stories saved to S3 and metadata written to DynamoDB in a single function call
- **Python 3.13 runtime** — uses `boto3`, `json`, `hashlib`, and `os` standard libraries

---

## Sample AWS Resources Created

- **Lambda function:** `story-teller-cb599c80`
- **S3 bucket:** `story-bucket-cb599c80`
- **DynamoDB table:** `story-table-cb599c80`
- **Bedrock model:** Amazon Nova Pro (Serverless)

---

## Author

Built as a hands-on cloud project to explore serverless architecture, generative AI integration, and AI-assisted development on AWS.
