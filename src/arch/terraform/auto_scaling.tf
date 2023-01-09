resource "aws_autoscaling_group" "lc_web_auto_scaling" {
  availability_zones        = ["us-west-2a", "us-west-2b"]
  capacity_rebalance        = true
  default_cooldown          = 300
  desired_capacity          = 1
  health_check_grace_period = 300
  health_check_type         = "EC2"
  max_size                  = 1
  metrics_granularity       = "1Minute"
  min_size                  = 1
  mixed_instances_policy {
    instances_distribution {
      on_demand_allocation_strategy            = "prioritized"
      on_demand_percentage_above_base_capacity = 100
      spot_allocation_strategy                 = "lowest-price"
      spot_instance_pools                      = 2
    }

    launch_template {
      launch_template_specification {
        launch_template_id   = "lt-02a49d72ea6e3c4c6"
        launch_template_name = "lc-web"
        version              = "$Default"
      }

      override {
        instance_type = "t2.micro"
      }

      override {
        instance_type = "t2.small"
      }

    }

  }

  name                    = "lc-web-auto-scaling"
  service_linked_role_arn = aws_iam_role.awsserviceroleforautoscaling.arn
  target_group_arns       = ["arn:aws:elasticloadbalancing:us-west-2:234659567514:targetgroup/lc-web-load-target-group/cfc5d03fcf07ae39"]
}

