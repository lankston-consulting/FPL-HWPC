resource "aws_cloudfront_distribution" "e146szegwxp2gu" {
  comment = "First attempt at load balancing (CDN) of hwpc inputs"
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cache_policy_id        = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    target_origin_id       = "hwpc.s3.us-west-2.amazonaws.com"
    viewer_protocol_policy = "allow-all"
  }

  enabled         = true
  http_version    = "http2and3"
  is_ipv6_enabled = true
  logging_config {
    bucket = "hwpc.s3.amazonaws.com"
    prefix = "cloudfront-logs/"
  }

  origin {
    connection_attempts = 3
    connection_timeout  = 10
    domain_name         = aws_s3_bucket.hwpc.bucket_regional_domain_name
    origin_id           = "hwpc.s3.us-west-2.amazonaws.com"
  }

  price_class = "PriceClass_100"
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }

  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1"
  }

  wait_for_deployment = true
}

