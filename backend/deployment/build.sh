docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --load \
  -f backend/deployment/Dockerfile \
  -t glyphic-backend:latest \
  .