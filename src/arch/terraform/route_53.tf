resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_3hyi67ovkw2qmjifx4ibncvwepgq624y__domainkey_hwpcarbon_com__cname" {
  name    = "3hyi67ovkw2qmjifx4ibncvwepgq624y._domainkey.hwpcarbon.com"
  records = ["3hyi67ovkw2qmjifx4ibncvwepgq624y.dkim.amazonses.com"]
  ttl     = 1800
  type    = "CNAME"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_hka3lawaoycykyisk2y3bjfny5y6r67m__domainkey_hwpcarbon_com__cname" {
  name    = "hka3lawaoycykyisk2y3bjfny5y6r67m._domainkey.hwpcarbon.com"
  records = ["hka3lawaoycykyisk2y3bjfny5y6r67m.dkim.amazonses.com"]
  ttl     = 1800
  type    = "CNAME"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_hwpcarbon_com__a" {
  alias {
    evaluate_target_health = true
    name                   = "hwpc-web-load-balancer-2124435053.us-west-2.elb.amazonaws.com"
    zone_id                = aws_alb.arn_aws_elasticloadbalancing_us_west_2_234659567514_loadbalancer_app_hwpc_web_load_balancer_477dd0231f613c7d.zone_id
  }

  name    = aws_ses_domain_mail_from.hwpcarbon_com.id
  type    = "A"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_hwpcarbon_com__ns" {
  name    = aws_ses_domain_mail_from.hwpcarbon_com.id
  records = ["ns-1250.awsdns-28.org.", "ns-202.awsdns-25.com.", "ns-600.awsdns-11.net.", "ns-2007.awsdns-58.co.uk."]
  ttl     = 60
  type    = "NS"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_hwpcarbon_com__soa" {
  name    = aws_ses_domain_mail_from.hwpcarbon_com.id
  records = ["ns-202.awsdns-25.com. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"]
  ttl     = 900
  type    = "SOA"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_qwq56u7otkntzrr24f3fbdzhgqkwtgvs__domainkey_hwpcarbon_com__cname" {
  name    = "qwq56u7otkntzrr24f3fbdzhgqkwtgvs._domainkey.hwpcarbon.com"
  records = ["qwq56u7otkntzrr24f3fbdzhgqkwtgvs.dkim.amazonses.com"]
  ttl     = 1800
  type    = "CNAME"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_record" "_hostedzone_z09617242mdjmuznpgxgp_www_hwpcarbon_com__a" {
  alias {
    evaluate_target_health = true
    name                   = "hwpc-web-load-balancer-2124435053.us-west-2.elb.amazonaws.com"
    zone_id                = aws_alb.arn_aws_elasticloadbalancing_us_west_2_234659567514_loadbalancer_app_hwpc_web_load_balancer_477dd0231f613c7d.zone_id
  }

  name    = "www.hwpcarbon.com"
  type    = "A"
  zone_id = aws_route53_zone._hostedzone_z09617242mdjmuznpgxgp.id
}

resource "aws_route53_zone" "_hostedzone_z09617242mdjmuznpgxgp" {
  comment = "HWPCarbon Web App"
  name    = aws_ses_domain_mail_from.hwpcarbon_com.id
}

