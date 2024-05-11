# gcloud auth login --cred-file=service-account.json
# gcloud config set project hatakeyamallm
# gcloud auth configure-docker us-east1-docker.pkg.dev
docker build -t us-east1-docker.pkg.dev/hatakeyamallm/cloud-run-commoncrawl/crawler:latest .
docker push us-east1-docker.pkg.dev/hatakeyamallm/cloud-run-commoncrawl/crawler:latest