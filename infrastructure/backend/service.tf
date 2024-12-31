
provider "kubernetes" {
  host                   = aws_eks_cluster.eks_cluster.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.eks_cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

resource "kubernetes_namespace" "namespace" {
  metadata {
    name = "glyphic"
  }
}

resource "kubernetes_secret" "anthropic_api" {
  metadata {
    name      = "anthropic-api"
    namespace = kubernetes_namespace.namespace.metadata[0].name
  }

  data = {
    key = var.anthropic_api_key
  }
}


resource "kubernetes_deployment" "deployment" {
  metadata {
    name      = "glyphic-backend"
    namespace = kubernetes_namespace.namespace.metadata[0].name
    labels = {
      app = "glyphic-backend"
    }
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "glyphic-backend"
      }
    }
    template {
      metadata {
        labels = {
          app = "glyphic-backend"
        }
      }
      spec {
        container {
          env {
            name = "ANTHROPIC_API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.anthropic_api.metadata[0].name
                key  = "key"
              }
            }
          }

          name  = "glyphic-backend"
          image = "619071355874.dkr.ecr.eu-north-1.amazonaws.com/glyphic-backend${var.image_selection}"
        }

      }
    }
  }
}

resource "kubernetes_service" "service" {
  metadata {
    name      = "glyphic-backend-service"
    namespace = kubernetes_namespace.namespace.metadata[0].name
  }

  spec {
    selector = {
      app = "glyphic-backend"
    }

    type = "LoadBalancer"

    port {
      port        = 80
      target_port = 80
    }
  }
}