provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}


resource "google_compute_global_forwarding_rule" "default" {
  name                  = "${var.resource_id}-forwarding-rule"
  target                = google_compute_target_https_proxy.default.id
  port_range            = "443"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

resource "google_compute_target_https_proxy" "default" {
  name             = "${var.resource_id}-https-proxy"
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

resource "google_compute_managed_ssl_certificate" "default" {
  name = "${var.resource_id}-ssl-certificate"
  managed {
    domains = [var.domain]
  }
}

resource "google_compute_url_map" "default" {
  name = var.resource_id

  default_service = google_compute_backend_service.default.self_link
}

resource "google_compute_backend_service" "default" {
  name                  = "${var.resource_id}-backend-service"
  protocol              = "HTTPS"
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group = google_compute_region_network_endpoint_group.cloud_run_neg.self_link
  }

}

resource "google_compute_region_network_endpoint_group" "cloud_run_neg" {
  name                  = "${var.cloud_run_service}-serverless-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region == null ? var.gcp_region : var.region
  cloud_run {
    service = var.cloud_run_service
  }
}

output "ip_address" {
  value = google_compute_global_forwarding_rule.default.ip_address
}

output "registered_domain" {
  value = var.domain
}

output "ssl_certificate_id" {

  value = google_compute_managed_ssl_certificate.default.id
}


output "gcp_id" {
  value = google_compute_url_map.default.id
}
