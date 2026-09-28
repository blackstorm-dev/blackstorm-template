output "bucket" {
  value = module.bucket.name
}

output "endpoint" {
  value = "https://${module.bucket.region}.digitaloceanspaces.com"
}
