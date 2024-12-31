docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -f backend/deployment/Dockerfile \
  -t 619071355874.dkr.ecr.eu-north-1.amazonaws.com/glyphic-backend:$(git rev-parse --short HEAD) \
  -t 619071355874.dkr.ecr.eu-north-1.amazonaws.com/glyphic-backend:latest \
  .