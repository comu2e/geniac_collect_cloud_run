REPOSITORY_NAME=cc-repo
REGION=us-central1
PROJECT_ID=common-crawler
# gcloud artifacts repositories create $REPOSITORY_NAME --location=$REGION --repository-format=docker --project=$PROJECT_ID

gcloud builds submit --region=us-central1 --config=cloudbuild.yaml
