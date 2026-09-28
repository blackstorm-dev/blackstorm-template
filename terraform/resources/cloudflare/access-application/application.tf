resource "cloudflare_zero_trust_access_policy" "allow" {
  account_id = var.account_id
  name       = "${var.name}: allowed emails"
  decision   = "allow"
  include    = [for e in var.allowed_emails : { email = { email = e } }]
}

resource "cloudflare_zero_trust_access_application" "this" {
  account_id       = var.account_id
  name             = var.name
  type             = "self_hosted"
  domain           = var.domain
  session_duration = var.session_duration
  policies = [{
    id = cloudflare_zero_trust_access_policy.allow.id
  }]
}
