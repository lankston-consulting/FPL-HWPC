resource "aws_s3_bucket" "hwpc" {
  arn            = "arn:aws:s3:::hwpc"
  bucket         = "hwpc"
  hosted_zone_id = "Z3BJ6K6RIION7M"
}

resource "aws_s3_bucket" "hwpc_output" {
  arn            = "arn:aws:s3:::hwpc-output"
  bucket         = "hwpc-output"
  hosted_zone_id = "Z3BJ6K6RIION7M"
}
