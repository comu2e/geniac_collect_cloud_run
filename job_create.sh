REGION=us-central1
PROJECT_ID=common-crawler
JOB_NAME=crawl_crawler

gcloud beta run jobs create $JOB_NAME \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/crawler/$JOB_NAME:v1 \
  --tasks=2 \
  --task-timeout=10m \
  --set-env-vars=BUCKET_NAME=scrape_keyword-$PROJECT_ID \
  --service-account=scrape_keyword-sa@$PROJECT_ID.iam.gserviceaccount.com
