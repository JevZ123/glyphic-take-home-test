variable "region" {
  type    = string
  default = "eu-north-1"
}

variable "account_id" {
  type    = string
  default = "619071355874"
}

variable "image_selection" {
  description = "SHA or :tag"
  type        = string
  default     = ":latest"
}

variable "anthropic_api_key" {
  type = string
}


