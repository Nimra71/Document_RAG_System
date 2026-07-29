# Deploying to Google Cloud Run (Free Tier)

One-time setup — after this, every `git push` to `main` auto-deploys.

## 1. Create a GCP account and project

1. Go to https://console.cloud.google.com and sign up (new accounts get $300 free credit)
2. Create a new project, note its **Project ID** (not the display name — the ID, e.g. `document-rag-123456`)

## 2. Enable required APIs

In the Cloud Console, enable:
- Cloud Run API
- Artifact Registry API
- IAM API

(Or via `gcloud`: `gcloud services enable run.googleapis.com artifactregistry.googleapis.com iam.googleapis.com`)

## 3. Create an Artifact Registry repo (to store your Docker images)

```
gcloud artifacts repositories create rag-repo \
  --repository-format=docker \
  --location=us-central1
```

## 4. Create a service account for GitHub Actions to deploy with

```
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Then create a key file for it:
```
gcloud iam service-accounts keys create github-key.json \
  --iam-account=github-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

This downloads `github-key.json` — you'll paste its contents into GitHub in step 6.
**Never commit this file to your repo.**

## 5. Store your Groq API key in GCP Secret Manager

```
echo -n "your_groq_api_key" | gcloud secrets create GROQ_API_KEY --data-file=-
```

Grant your service account access (already covered by the `secretAccessor` role above).

## 6. Add GitHub repo secrets

In your GitHub repo: Settings → Secrets and variables → Actions → New repository secret. Add:

- `GCP_PROJECT_ID` — your project ID from step 1
- `GCP_SA_KEY` — paste the **entire contents** of `github-key.json` from step 4

## 7. Push to main

```
git add .
git commit -m "Add production FastAPI + Docker + CI/CD"
git push origin main
```

GitHub Actions will build the Docker image, push it to Artifact Registry, and deploy
it to Cloud Run automatically. Check the "Actions" tab on GitHub to watch progress.
Once it finishes, Cloud Run gives you a live URL — that's your deployed API.

## Testing the deployed app

Visit `https://your-service-url.run.app/docs` for the same interactive API docs you
used locally, now live on the internet.
