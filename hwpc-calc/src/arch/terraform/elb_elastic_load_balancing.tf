resource "aws_alb" "arn_aws_elasticloadbalancing_us_west_2_234659567514_loadbalancer_app_hwpc_web_load_balancer_477dd0231f613c7d" {
  access_logs {
    bucket = ""
  }

  desync_mitigation_mode           = "defensive"
  enable_cross_zone_load_balancing = true
  enable_http2                     = true
  idle_timeout                     = 60
  ip_address_type                  = "ipv4"
  load_balancer_type               = "application"
  name                             = "hwpc-web-load-balancer"
  security_groups                  = [aws_security_group.sg_0022db799b846e775.id]
  subnet_mapping {
    subnet_id = aws_subnet.subnet_0a67a553e8d4a6e46.id
  }

  subnet_mapping {
    subnet_id = aws_subnet.subnet_0d21162897dfdc2ad.id
  }

  subnets = ["subnet-0d21162897dfdc2ad", "subnet-0a67a553e8d4a6e46"]
}

resource "aws_alb_listener" "arn_aws_elasticloadbalancing_us_west_2_234659567514_listener_app_hwpc_web_load_balancer_477dd0231f613c7d_22cde81b9668be6c" {
  default_action {
    order = 1
    redirect {
      host        = "#{host}"
      path        = "/#{path}"
      port        = "443"
      protocol    = "HTTPS"
      query       = "#{query}"
      status_code = "HTTP_301"
    }

    type = "redirect"
  }

  load_balancer_arn = aws_alb.arn_aws_elasticloadbalancing_us_west_2_234659567514_loadbalancer_app_hwpc_web_load_balancer_477dd0231f613c7d.id
  port              = 80
  protocol          = "HTTP"
}

resource "aws_alb_listener" "arn_aws_elasticloadbalancing_us_west_2_234659567514_listener_app_hwpc_web_load_balancer_477dd0231f613c7d_8f96eb59f322ebc3" {
  certificate_arn = "arn:aws:acm:us-west-2:234659567514:certificate/664bd509-5a1a-4353-a01e-dfdd87c7c64d"
  default_action {
    order            = 1
    target_group_arn = aws_alb_target_group.arn_aws_elasticloadbalancing_us_west_2_234659567514_targetgroup_hwpc_web_fargate_tg_59c5cc26133b5efa.id
    type             = "forward"
  }

  load_balancer_arn = aws_alb.arn_aws_elasticloadbalancing_us_west_2_234659567514_loadbalancer_app_hwpc_web_load_balancer_477dd0231f613c7d.id
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
}

resource "aws_alb_listener_rule" "arn_aws_elasticloadbalancing_us_west_2_234659567514_listener_rule_app_hwpc_web_load_balancer_477dd0231f613c7d_22cde81b9668be6c_bf3272a871aeb1af" {
  action {
    order = 1
    redirect {
      host        = "#{host}"
      path        = "/#{path}"
      port        = "443"
      protocol    = "HTTPS"
      query       = "#{query}"
      status_code = "HTTP_301"
    }

    type = "redirect"
  }

  condition    = []
  listener_arn = aws_alb_listener.arn_aws_elasticloadbalancing_us_west_2_234659567514_listener_app_hwpc_web_load_balancer_477dd0231f613c7d_22cde81b9668be6c.id
  priority     = 99999
}

resource "aws_alb_listener_rule" "arn_aws_elasticloadbalancing_us_west_2_234659567514_listener_rule_app_hwpc_web_load_balancer_477dd0231f613c7d_8f96eb59f322ebc3_f2eef01f86b3eccf" {
  action {
    order            = 1
    target_group_arn = aws_alb_target_group.arn_aws_elasticloadbalancing_us_west_2_234659567514_targetgroup_hwpc_web_fargate_tg_59c5cc26133b5efa.id
    type             = "forward"
  }

  condition    = []
  listener_arn = aws_alb_listener.arn_aws_elasticloadbalancing_us_west_2_234659567514_listener_app_hwpc_web_load_balancer_477dd0231f613c7d_8f96eb59f322ebc3.id
  priority     = 99999
}

resource "aws_alb_target_group" "arn_aws_elasticloadbalancing_us_west_2_234659567514_targetgroup_hwpc_web_fargate_tg_59c5cc26133b5efa" {
  deregistration_delay = "300"
  health_check {
    enabled             = true
    healthy_threshold   = 5
    interval            = 30
    matcher             = "200"
    path                = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  load_balancing_algorithm_type = "round_robin"
  name                          = "hwpc-web-fargate-tg"
  port                          = 80
  protocol                      = "HTTP"
  protocol_version              = "HTTP1"
  stickiness {
    cookie_duration = 86400
    type            = "lb_cookie"
  }

  target_type = "ip"
  vpc_id      = aws_vpc.vpc_0012250a7646d8885.id
}

resource "aws_alb_target_group_attachment" "Geczn" {
  port             = 80
  target_group_arn = aws_alb_target_group.arn_aws_elasticloadbalancing_us_west_2_234659567514_targetgroup_hwpc_web_fargate_tg_59c5cc26133b5efa.id
  target_id        = "172.31.28.192"
}

resource "aws_alb_target_group_attachment" "NOvQE" {
  port             = 443
  target_group_arn = aws_alb_target_group.arn_aws_elasticloadbalancing_us_west_2_234659567514_targetgroup_hwpc_web_fargate_tg_59c5cc26133b5efa.id
  target_id        = "172.31.44.193"
}

