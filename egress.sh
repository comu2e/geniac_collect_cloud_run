# Define variables
SUBNET_NAME="cloudrun-subnet"
RANGE="10.124.0.0/18"
NETWORK_NAME="cloudrun-job-network"
REGION="us-central1"
ROUTER_NAME="cloudrun-router"
ORIGIN_IP_NAME="origin-cloud-run-ip"
NAT_NAME="cloudrun-nat"

# Create a custom network
gcloud compute networks create "$NETWORK_NAME" --subnet-mode=custom

# Create a subnet within the custom network
gcloud compute networks subnets create "$SUBNET_NAME" \
  --range="$RANGE" --network="$NETWORK_NAME" --region="$REGION"

# Create a router for the network
gcloud compute routers create "$ROUTER_NAME" \
  --network="$NETWORK_NAME" --region="$REGION"

# Create an external IP address for the NAT
gcloud compute addresses create "$ORIGIN_IP_NAME" --region="$REGION"

# Create and configure a NAT with custom IP ranges and an external IP pool
gcloud compute routers nats create "$NAT_NAME" \
  --router="$ROUTER_NAME" \
  --region="$REGION" \
  --nat-custom-subnet-ip-ranges="$SUBNET_NAME" \
  --nat-external-ip-pool="$ORIGIN_IP_NAME"
