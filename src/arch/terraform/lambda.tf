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
      AWS_CLUSTER_ARN          = aws_ecs_service.hwpc_web_fargate_cluster_hwpc_web_service_1.cluster
      AWS_CONTAINER_IMAGE      = "234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:worker"
      AWS_SECURITY_GROUP       = aws_security_group.sg_0356d5f4aa0d5fbe8.id
      DASK_N_WORKERS           = "24"
      DASK_SCEDULER_CPU        = "4096"
      DASK_SCEDULER_MEM        = "8192"
      DASK_USE_FARGATE         = "1"
      DASK_WORKER_CPU          = "2048"
      DASK_WORKER_MEM          = "4096"
      HWPC__CDN_URI            = "https://d2yxltrtv1a9pi.cloudfront.net/"
      HWPC__DEBUG__MODE        = "0"
      HWPC__FIRST_RECYCLE_YEAR = "1970"
      HWPC__PURE_S3            = aws_cloudfront_distribution.e146szegwxp2gu.in_progress_validation_batches
      HWPC__RECURSE_LIMIT      = "1"
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
  source_code_hash               = "40l33ySDXfJQUHV7/HEkwsn9IatV+Jla1rfV8faTR88="
  timeout                        = 3
  tracing_config {
    mode = "PassThrough"
  }

}

