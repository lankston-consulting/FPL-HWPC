resource "aws_route53_resolver_rule_association" "rslvr_autodefined_assoc_vpc_0012250a7646d8885_internet_resolver" {
  name             = "System Rule Association"
  resolver_rule_id = "rslvr-autodefined-rr-internet-resolver"
  vpc_id           = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_route53_resolver_rule_association" "rslvr_autodefined_assoc_vpc_0da0dfeb6795dec34_internet_resolver" {
  name             = "System Rule Association"
  resolver_rule_id = "rslvr-autodefined-rr-internet-resolver"
  vpc_id           = aws_vpc.ecs_hwpc_web_cluster___vpc.id
}

