# resource "aws_s3_bucket" "cf_templates_ui1evhwv02nm_us_west_2" {
#   arn            = "arn:aws:s3:::cf-templates-ui1evhwv02nm-us-west-2"
#   bucket         = "cf-templates-ui1evhwv02nm-us-west-2"
#   hosted_zone_id = "Z3BJ6K6RIION7M"
# }

# resource "aws_s3_bucket" "codepipeline_us_west_2_323442444403" {
#   arn            = "arn:aws:s3:::codepipeline-us-west-2-323442444403"
#   bucket         = "codepipeline-us-west-2-323442444403"
#   hosted_zone_id = "Z3BJ6K6RIION7M"
# }

resource "aws_s3_bucket" "hwpc" {
  #   arn            = "aws:s3:::hwpc"
  bucket = "hwpc"
  #   hosted_zone_id = "Z3BJ6K6RIION7M"
}

resource "aws_s3_bucket_public_access_block" "example-public-access-block" {
  bucket = "hwpc"

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "hwpc_output" {
  #   arn            = "aws:s3:::hwpc-output"
  bucket = "hwpc-output"
  #   hosted_zone_id = "Z3BJ6K6RIION7M"
}
