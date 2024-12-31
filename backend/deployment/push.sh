aws ecr get-login-password --region eu-north-1 \
| docker login \
  --username AWS \
  --password-stdin 619071355874.dkr.ecr.eu-north-1.amazonaws.com

LATEST_COMMIT_HASH=$(git rev-parse --short HEAD)

TAGS=("latest" "$LATEST_COMMIT_HASH")

for TAG in "${TAGS[@]}"; do
  ECR_TAG="619071355874.dkr.ecr.eu-north-1.amazonaws.com/glyphic-backend:${TAG}"
  docker tag glyphic-backend:latest "$ECR_TAG"
  docker push "$ECR_TAG"
done