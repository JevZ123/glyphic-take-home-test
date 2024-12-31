resource "aws_ecr_repository" "this" {
  name = "glyphic-backend"

  image_scanning_configuration {
    scan_on_push = true
  }
}