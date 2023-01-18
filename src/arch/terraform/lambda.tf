resource "aws_lambda_function" "get_user_input" {
  tags = {
    "lambda-console:blueprint" = "s3-get-object-python"
  }

  tags_all = {
    "lambda-console:blueprint" = "s3-get-object-python"
  }

  architectures = ["x86_64"]
  description   = "An Amazon S3 trigger that retrieves metadata for the object that has been updated."
  environment {
    variables = {
      AWS_CLUSTER_ARN          = "hwpc-web-fargate-cluster"
      AWS_SCHEDULER_ARN        = "hwpc-dask-scheduler"
      AWS_SECURITY_GROUP       = aws_security_group.sg_0356d5f4aa0d5fbe8.id
      AWS_SUBNET_ID            = aws_subnet.subnet_00c7b79155a9bbab8.id
      AWS_VPC_ID               = aws_vpc.vpc_0012250a7646d8885.id
      AWS_WORKER_ARN           = "hwpc-dask-worker"
      DASK_N_WORKERS           = "40"
      DASK_USE_FARGATE         = "1"
      HWPC__CDN_URI            = "https://d2yxltrtv1a9pi.cloudfront.net/"
      HWPC__DEBUG__MODE        = "0"
      HWPC__FIRST_RECYCLE_YEAR = "1970"
      HWPC__PURE_S3            = aws_cloudfront_distribution.e146szegwxp2gu.in_progress_validation_batches
      HWPC__RECURSE_LIMIT      = aws_ecs_service.hwpc_web_fargate_cluster_hwpc_web_service_1.desired_count
      S3_INPUT_BUCKET          = aws_s3_bucket.hwpc.id
      S3_OUTPUT_BUCKET         = aws_s3_bucket.hwpc_output.id
    }

  }

  ephemeral_storage {
    size = 512
  }

  function_name                  = "get_user_input"
  handler                        = "lambda_function.lambda_handler"
  memory_size                    = 128
  package_type                   = "Zip"
  reserved_concurrent_executions = -1
  role                           = aws_iam_role.read_bucket.arn
  runtime                        = "python3.7"
  source_code_hash               = "OXuaKcKbrolRJNqLmBmD4VQlpyiMUMkVqzxj9n495Cs="
  timeout                        = 3
  tracing_config {
    mode = "PassThrough"
  }

}

