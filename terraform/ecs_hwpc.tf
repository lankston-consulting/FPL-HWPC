resource "aws_ecs_cluster" "hwpc_cluster" {
  name = "hwpc-cluster"
  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

resource "aws_ecs_service" "hwpc_cluster_hwpc_web_service" {
  cluster = "arn:aws:ecs:us-west-2:234659567514:cluster/hwpc-cluster"
  deployment_circuit_breaker {
    enable   = false
    rollback = false
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  desired_count                      = 1
  enable_ecs_managed_tags            = true
  iam_role                           = "aws-service-role"
  launch_type                        = "FARGATE"
  load_balancer {
    container_name   = "hwpc-web"
    container_port   = 80
    target_group_arn = aws_alb_target_group.arn_aws_elasticloadbalancing_us_west_2_234659567514_targetgroup_hwpc_web_fargate_tg_59c5cc26133b5efa.id
  }

  name = "hwpc-web-service"
  network_configuration {
    assign_public_ip = true
    security_groups  = [aws_security_group.sg_0022db799b846e775.id]
    subnets          = [aws_subnet.subnet_0d21162897dfdc2ad.id, aws_subnet.subnet_0a67a553e8d4a6e46.id]
  }

  platform_version    = "LATEST"
  propagate_tags      = "NONE"
  scheduling_strategy = "REPLICA"
  task_definition     = "hwpcweb:5"
}
