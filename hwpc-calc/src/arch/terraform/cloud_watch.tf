resource "aws_cloudwatch_metric_alarm" "targettracking_service_hwpc_web_fargate_cluster_hwpc_web_service_1_alarmhigh_dc2b17c4_5350_414f_a74e_74308d1b9f1b" {
  dimensions = {
    ClusterName = "hwpc-web-fargate-cluster"
    ServiceName = aws_ecs_service.hwpc_web_fargate_cluster_hwpc_web_service_1.name
  }

  actions_enabled     = true
  alarm_actions       = ["arn:aws:autoscaling:us-west-2:234659567514:scalingPolicy:714a6818-94cd-4aea-b0a4-fb4bb2bfb17f:resource/ecs/service/hwpc-web-fargate-cluster/hwpc-web-service-1:policyName/hwpc-web-scaling-policy:createdBy/df9745ae-5384-4d3d-bc7c-7436dba9a7cb"]
  alarm_description   = "DO NOT EDIT OR DELETE. For TargetTrackingScaling policy arn:aws:autoscaling:us-west-2:234659567514:scalingPolicy:714a6818-94cd-4aea-b0a4-fb4bb2bfb17f:resource/ecs/service/hwpc-web-fargate-cluster/hwpc-web-service-1:policyName/hwpc-web-scaling-policy:createdBy/df9745ae-5384-4d3d-bc7c-7436dba9a7cb."
  alarm_name          = "TargetTracking-service/hwpc-web-fargate-cluster/hwpc-web-service-1-AlarmHigh-dc2b17c4-5350-414f-a74e-74308d1b9f1b"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 70
  treat_missing_data  = "missing"
  unit                = "Percent"
}

resource "aws_cloudwatch_metric_alarm" "targettracking_service_hwpc_web_fargate_cluster_hwpc_web_service_1_alarmlow_21295b3a_3bf3_49f1_bf69_35180c5e50f5" {
  dimensions = {
    ClusterName = "hwpc-web-fargate-cluster"
    ServiceName = aws_ecs_service.hwpc_web_fargate_cluster_hwpc_web_service_1.name
  }

  actions_enabled     = true
  alarm_actions       = ["arn:aws:autoscaling:us-west-2:234659567514:scalingPolicy:714a6818-94cd-4aea-b0a4-fb4bb2bfb17f:resource/ecs/service/hwpc-web-fargate-cluster/hwpc-web-service-1:policyName/hwpc-web-scaling-policy:createdBy/df9745ae-5384-4d3d-bc7c-7436dba9a7cb"]
  alarm_description   = "DO NOT EDIT OR DELETE. For TargetTrackingScaling policy arn:aws:autoscaling:us-west-2:234659567514:scalingPolicy:714a6818-94cd-4aea-b0a4-fb4bb2bfb17f:resource/ecs/service/hwpc-web-fargate-cluster/hwpc-web-service-1:policyName/hwpc-web-scaling-policy:createdBy/df9745ae-5384-4d3d-bc7c-7436dba9a7cb."
  alarm_name          = "TargetTracking-service/hwpc-web-fargate-cluster/hwpc-web-service-1-AlarmLow-21295b3a-3bf3-49f1-bf69-35180c5e50f5"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 15
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 63
  treat_missing_data  = "missing"
  unit                = "Percent"
}

