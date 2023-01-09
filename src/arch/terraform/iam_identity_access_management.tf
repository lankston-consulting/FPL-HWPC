resource "aws_iam_access_key" "akiatniwm26nchl4dpb6" {
  status = "Active"
  user   = aws_iam_user.administrator.id
}

resource "aws_iam_access_key" "akiatniwm26ndiizsrtk" {
  status = "Active"
  user   = aws_iam_user.dtuser.id
}

resource "aws_iam_access_key" "akiatniwm26nfv4gy5uv" {
  status = "Active"
  user   = aws_iam_user.hwpc_sa.id
}

resource "aws_iam_access_key" "akiatniwm26ngnbdtqg3" {
  status = "Active"
  user   = aws_iam_user.robb.id
}

resource "aws_iam_access_key" "akiatniwm26nnehoedd2" {
  status = "Active"
  user   = aws_iam_user.clairespain.id
}

resource "aws_iam_access_key" "akiatniwm26npc5banjs" {
  status = "Active"
  user   = aws_iam_user.coltongerth.id
}

resource "aws_iam_group" "administrators" {
  name = "Administrators"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_group" "s3_to_google_drive" {
  name = "s3-to-google-drive"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_group_membership" "administrators" {
  group = "Administrators"
  name  = ""
  users = [aws_iam_user.clairespain.id, aws_iam_user.robb.id, aws_iam_user.administrator.id, aws_iam_user.coltongerth.id]
}

resource "aws_iam_group_membership" "s3_to_google_drive" {
  group = "s3-to-google-drive"
  name  = ""
  users = [aws_iam_user.clairespain.id]
}

resource "aws_iam_group_policy_attachment" "administrators_arn_aws_iam__aws_policy_administratoraccess" {
  group      = aws_iam_group.administrators.id
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_amazons3fullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_amazonssmfullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMFullAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_awscloudformationfullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_awscloudshellfullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/AWSCloudShellFullAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_awslambda_fullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_cloudwatchfullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_group_policy_attachment" "s3_to_google_drive_arn_aws_iam__aws_policy_iamfullaccess" {
  group      = aws_iam_group.s3_to_google_drive.id
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_contact_ses_policy" {
  description = "basic SES write permissions for the contact email contact@hwpcarbon.com"
  name        = "contact-ses-policy"
  path        = "/"
  policy      = "{\"Statement\":[{\"Action\":\"ses:SendRawEmail\",\"Condition\":{\"StringEqualsIgnoreCase\":{\"ses:FromAddress\":[\"contact@hwpcarbon.com\"]}},\"Effect\":\"Allow\",\"Resource\":\"*\"}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_dask_fargate_policy" {
  description = "To create a FargateCluster the cluster manager will need to use various AWS resources ranging from IAM roles to VPCs to ECS tasks. Depending on your use case you may want the cluster to create all of these for you, or you may wish to specify them yourself ahead of time. Here is the full minimal IAM policy that you need to create the whole cluster."
  name        = "dask-fargate-policy"
  path        = "/"
  policy      = "{\"Statement\":[{\"Action\":[\"ec2:AuthorizeSecurityGroupIngress\",\"ec2:CreateSecurityGroup\",\"ec2:CreateTags\",\"ec2:DescribeNetworkInterfaces\",\"ec2:DescribeSecurityGroups\",\"ec2:DescribeSubnets\",\"ec2:DescribeVpcs\",\"ec2:DeleteSecurityGroup\",\"ecs:CreateCluster\",\"ecs:DescribeTasks\",\"ecs:ListAccountSettings\",\"ecs:RegisterTaskDefinition\",\"ecs:RunTask\",\"ecs:StopTask\",\"ecs:ListClusters\",\"ecs:DescribeClusters\",\"ecs:DeleteCluster\",\"ecs:ListTaskDefinitions\",\"ecs:DescribeTaskDefinition\",\"ecs:DeregisterTaskDefinition\",\"iam:AttachRolePolicy\",\"iam:CreateRole\",\"iam:TagRole\",\"iam:PassRole\",\"iam:DeleteRole\",\"iam:ListRoles\",\"iam:ListRoleTags\",\"iam:ListAttachedRolePolicies\",\"iam:DetachRolePolicy\",\"logs:DescribeLogGroups\",\"logs:GetLogEvents\",\"logs:CreateLogGroup\",\"logs:PutRetentionPolicy\"],\"Effect\":\"Allow\",\"Resource\":[\"*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_elasitcipuserrole" {
  description = "Allows allocating and associating elastic IP addresses."
  name        = "ElasitcIPUserRole"
  path        = "/"
  policy      = "{\"Statement\":[{\"Action\":[\"ec2:AllocateAddress\",\"ec2:AssociateAddress\"],\"Effect\":\"Allow\",\"Resource\":\"*\"}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_hwpc_sa" {
  description = "List, Read, and Write permissions for specifically the hwpc bucket."
  name        = aws_iam_user.hwpc_sa.id
  path        = "/"
  policy      = "{\"Statement\":[{\"Action\":[\"logs:GetLogRecord\",\"logs:GetLogDelivery\",\"logs:ListLogDeliveries\",\"s3:GetObjectAcl\",\"logs:DeleteResourcePolicy\",\"logs:CancelExportTask\",\"logs:DeleteLogDelivery\",\"logs:DescribeQueryDefinitions\",\"s3:DeleteObject\",\"logs:DescribeResourcePolicies\",\"sts:GetServiceBearerToken\",\"logs:DescribeDestinations\",\"s3:PutObjectAcl\",\"logs:DescribeQueries\",\"s3:GetBucketPublicAccessBlock\",\"s3:GetBucketPolicyStatus\",\"ecr-public:GetAuthorizationToken\",\"s3:ListAccessPoints\",\"logs:StopQuery\",\"logs:TestMetricFilter\",\"logs:DeleteQueryDefinition\",\"logs:PutQueryDefinition\",\"s3:GetBucketAcl\",\"logs:Link\",\"logs:CreateLogDelivery\",\"s3:PutObject\",\"s3:GetObject\",\"logs:PutResourcePolicy\",\"logs:DescribeExportTasks\",\"s3:GetAccountPublicAccessBlock\",\"logs:GetQueryResults\",\"s3:ListAllMyBuckets\",\"logs:UpdateLogDelivery\",\"s3:GetBucketLocation\"],\"Effect\":\"Allow\",\"Resource\":\"*\",\"Sid\":\"VisualEditor0\"},{\"Action\":[\"ecr-public:DescribeImageTags\",\"ecr-public:DescribeImages\",\"ecr-public:DescribeRepositories\",\"logs:*\",\"ecr-public:DescribeRegistries\",\"ecr-public:GetRepositoryCatalogData\",\"ecr-public:GetRegistryCatalogData\",\"s3:ListBucket\",\"ecr-public:GetRepositoryPolicy\",\"ecr-public:BatchCheckLayerAvailability\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:*:234659567514:log-group:*\",\"arn:aws:s3:::hwpc\",\"arn:aws:s3:::hwpc-output\",\"arn:aws:ecr-public::234659567514:repository/*\",\"arn:aws:ecr-public::234659567514:registry/*\"],\"Sid\":\"VisualEditor1\"},{\"Action\":[\"s3:*Object\",\"logs:*\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:s3:::hwpc/*\",\"arn:aws:s3:::hwpc-output/*\",\"arn:aws:logs:*:234659567514:log-group:*:log-stream:*\",\"arn:aws:logs:*:234659567514:destination:*\"],\"Sid\":\"VisualEditor2\"}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_05a402ec_d770_42fe_848a_5e6e6d2574fe" {
  name   = "AWSLambdaBasicExecutionRole-05a402ec-d770-42fe-848a-5e6e6d2574fe"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":\"logs:CreateLogGroup\",\"Effect\":\"Allow\",\"Resource\":\"arn:aws:logs:us-west-2:234659567514:*\"},{\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:us-west-2:234659567514:log-group:/aws/lambda/get_user_json:*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2e75c241_3019_4862_aae0_2774e918b01e" {
  name   = "AWSLambdaBasicExecutionRole-2e75c241-3019-4862-aae0-2774e918b01e"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":\"logs:CreateLogGroup\",\"Effect\":\"Allow\",\"Resource\":\"arn:aws:logs:us-west-2:234659567514:*\"},{\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:us-west-2:234659567514:log-group:/aws/lambda/get_user_json:*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2eea173a_6a46_4768_9e63_23b58c209326" {
  name   = "AWSLambdaBasicExecutionRole-2eea173a-6a46-4768-9e63-23b58c209326"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":\"logs:CreateLogGroup\",\"Effect\":\"Allow\",\"Resource\":\"arn:aws:logs:us-west-2:234659567514:*\"},{\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:us-west-2:234659567514:log-group:/aws/lambda/get_user_input:*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_402dc6ad_e0b0_414e_b565_faf7191fa745" {
  name   = "AWSLambdaBasicExecutionRole-402dc6ad-e0b0-414e-b565-faf7191fa745"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":\"logs:CreateLogGroup\",\"Effect\":\"Allow\",\"Resource\":\"arn:aws:logs:us-west-2:234659567514:*\"},{\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:us-west-2:234659567514:log-group:/aws/lambda/update-task-dns:*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_9da34040_213b_4f9f_bfa0_3a2f368f6731" {
  name   = "AWSLambdaBasicExecutionRole-9da34040-213b-4f9f-bfa0-3a2f368f6731"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":\"logs:CreateLogGroup\",\"Effect\":\"Allow\",\"Resource\":\"arn:aws:logs:us-east-1:234659567514:*\"},{\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:us-east-1:234659567514:log-group:/aws/lambda/get_user_json:*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4" {
  name   = "AWSLambdaBasicExecutionRole-accd95e3-9f91-4f08-9ba9-233d317599a4"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":\"logs:CreateLogGroup\",\"Effect\":\"Allow\",\"Resource\":\"arn:aws:logs:us-east-1:234659567514:*\"},{\"Action\":[\"logs:CreateLogStream\",\"logs:PutLogEvents\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:logs:us-east-1:234659567514:log-group:/aws/lambda/s3_demo:*\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_9d1c84cf_c232_4998_896f_5dfd1e7a7868" {
  name   = "AWSLambdaS3ExecutionRole-9d1c84cf-c232-4998-896f-5dfd1e7a7868"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":[\"s3:GetObject\"],\"Effect\":\"Allow\",\"Resource\":\"arn:aws:s3:::*\"}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_cf95b68f_f26c_479b_911d_b5afba02d5ed" {
  name   = "AWSLambdaS3ExecutionRole-cf95b68f-f26c-479b-911d-b5afba02d5ed"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":[\"s3:GetObject\"],\"Effect\":\"Allow\",\"Resource\":\"arn:aws:s3:::*\"}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_fc6a086b_8130_486f_8c18_dd0d65011a1c" {
  name   = "AWSLambdaS3ExecutionRole-fc6a086b-8130-486f-8c18-dd0d65011a1c"
  path   = "/service-role/"
  policy = "{\"Statement\":[{\"Action\":[\"s3:GetObject\"],\"Effect\":\"Allow\",\"Resource\":\"arn:aws:s3:::*\"}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_policy" "arn_aws_iam__234659567514_policy_service_role_start_pipeline_execution_us_west_2_frontend_dep" {
  description = "Allows Amazon CloudWatch Events to automatically start a new execution in the frontend-dep pipeline when a change occurs"
  name        = "start-pipeline-execution-us-west-2-frontend-dep"
  path        = "/service-role/"
  policy      = "{\"Statement\":[{\"Action\":[\"codepipeline:StartPipelineExecution\"],\"Effect\":\"Allow\",\"Resource\":[\"arn:aws:codepipeline:us-west-2:234659567514:frontend-dep\"]}],\"Version\":\"2012-10-17\"}"
}

resource "aws_iam_role" "aws_quicksetup_stackset_local_administrationrole" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"cloudformation.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
    name   = "AssumeRole-AWS-QuickSetup-StackSet-Local-ExecutionRole"
    policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Action\":[\"sts:AssumeRole\"],\"Resource\":[\"arn:*:iam::*:role/AWS-QuickSetup-StackSet-Local-ExecutionRole\"],\"Effect\":\"Allow\"}]}"
  }

  max_session_duration = 3600
  name                 = "AWS-QuickSetup-StackSet-Local-AdministrationRole"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "aws_quicksetup_stackset_local_executionrole" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::234659567514:role/AWS-QuickSetup-StackSet-Local-AdministrationRole\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/AdministratorAccess"]
  max_session_duration = 3600
  name                 = "AWS-QuickSetup-StackSet-Local-ExecutionRole"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "awsserviceroleforamazonssm" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ssm.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Provides access to AWS Resources managed or used by Amazon SSM."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AmazonSSMServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForAmazonSSM"
  path                 = "/aws-service-role/ssm.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforapplicationautoscaling_ecsservice" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs.application-autoscaling.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSApplicationAutoscalingECSServicePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForApplicationAutoScaling_ECSService"
  path                 = "/aws-service-role/ecs.application-autoscaling.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforautoscaling" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"autoscaling.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Default Service-Linked Role enables access to AWS Services and Resources used or managed by Auto Scaling"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AutoScalingServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForAutoScaling"
  path                 = "/aws-service-role/autoscaling.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforcomputeoptimizer" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"compute-optimizer.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Allows ComputeOptimizer to call AWS services and collect workload details on your behalf."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/ComputeOptimizerServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForComputeOptimizer"
  path                 = "/aws-service-role/compute-optimizer.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforecs" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Role to enable Amazon ECS to manage your cluster."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AmazonECSServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForECS"
  path                 = "/aws-service-role/ecs.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforelasticloadbalancing" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"elasticloadbalancing.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Allows ELB to call AWS services on your behalf."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSElasticLoadBalancingServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForElasticLoadBalancing"
  path                 = "/aws-service-role/elasticloadbalancing.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforglobalaccelerator" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"globalaccelerator.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Allows Global Accelerator to call AWS services on customer's behalf"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSGlobalAcceleratorSLRPolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForGlobalAccelerator"
  path                 = "/aws-service-role/globalaccelerator.amazonaws.com/"
}

resource "aws_iam_role" "awsservicerolefororganizations" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"organizations.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Service-linked role used by AWS Organizations to enable integration of other AWS services with Organizations."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSOrganizationsServiceTrustPolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForOrganizations"
  path                 = "/aws-service-role/organizations.amazonaws.com/"
}

resource "aws_iam_role" "awsservicerolefors3storagelens" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"storage-lens.s3.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Service Linked Role for S3 Storage Lens"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/S3StorageLensServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForS3StorageLens"
  path                 = "/aws-service-role/storage-lens.s3.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforservicequotas" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"servicequotas.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "A service-linked role is required for Service Quotas to access your service limits."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/ServiceQuotasServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForServiceQuotas"
  path                 = "/aws-service-role/servicequotas.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforsso" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"sso.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Service-linked role used by AWS SSO to manage AWS resources, including IAM roles, policies and SAML IdP on your behalf."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSSSOServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForSSO"
  path                 = "/aws-service-role/sso.amazonaws.com/"
}

resource "aws_iam_role" "awsserviceroleforsupport" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"support.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Enables resource access for AWS to provide billing, administrative and support services"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSSupportServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForSupport"
  path                 = "/aws-service-role/support.amazonaws.com/"
}

resource "aws_iam_role" "awsservicerolefortrustedadvisor" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"trustedadvisor.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Access for the AWS Trusted Advisor Service to help reduce cost, increase performance, and improve security of your AWS environment."
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/aws-service-role/AWSTrustedAdvisorServiceRolePolicy"]
  max_session_duration = 3600
  name                 = "AWSServiceRoleForTrustedAdvisor"
  path                 = "/aws-service-role/trustedadvisor.amazonaws.com/"
}

resource "aws_iam_role" "cwe_role_us_west_2_frontend_dep" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"events.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_start_pipeline_execution_us_west_2_frontend_dep.id]
  max_session_duration = 3600
  name                 = "cwe-role-us-west-2-frontend-dep"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.path
}

resource "aws_iam_role" "ecsautoscalerole" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"application-autoscaling.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceAutoscaleRole"]
  max_session_duration = 3600
  name                 = "ecsAutoscaleRole"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "ecstaskexecutionrole" {
  assume_role_policy = "{\"Version\":\"2008-10-17\",\"Statement\":[{\"Sid\":\"\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs-tasks.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"]
  max_session_duration = 3600
  name                 = "ecsTaskExecutionRole"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "elasticipuserrole" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::234659567514:root\"},\"Action\":\"sts:AssumeRole\",\"Condition\":{}}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_elasitcipuserrole.id]
  max_session_duration = 3600
  name                 = "ElasticIPUserRole"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "get_user_json_role_6laoudf0" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_9da34040_213b_4f9f_bfa0_3a2f368f6731.id]
  max_session_duration = 3600
  name                 = "get_user_json-role-6laoudf0"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.path
}

resource "aws_iam_role" "get_user_json_role_zjiw3n1t" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_05a402ec_d770_42fe_848a_5e6e6d2574fe.id]
  max_session_duration = 3600
  name                 = "get_user_json-role-zjiw3n1t"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.path
}

resource "aws_iam_role" "googledrive_lambdaexecutionrole" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowLambdaServiceToAssumeRole\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
    name   = "root"
    policy = "{\n    \"Version\": \"2012-10-17\",\n    \"Statement\": [\n        {\n            \"Action\": [\n                \"s3:GetObject\",\n                \"s3:GetObjectAcl\"\n            ],\n            \"Resource\": [\n                \"arn:aws:s3:::s3-to-google-drive-hwpc/*\",\n                \"arn:aws:s3:::hwpc-output/*\"\n            ],\n            \"Effect\": \"Allow\"\n        },\n        {\n            \"Sid\": \"ListObjectsInBucket\",\n            \"Effect\": \"Allow\",\n            \"Action\": \"s3:ListBucket\",\n            \"Resource\": [\n                \"arn:aws:s3:::hwpc-output\"\n            ]\n        },\n        {\n            \"Action\": [\n                \"ssm:GetParameter\"\n            ],\n            \"Resource\": \"arn:aws:ssm:us-west-2:234659567514:parameter/google-*\",\n            \"Effect\": \"Allow\"\n        }\n    ]\n}"
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  max_session_duration = 3600
  name                 = "GoogleDrive-LambdaExecutionRole"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "hwpc_web_fargate_cluster_execution_role" {
  tags = {
    cluster   = "hwpc-web-fargate-cluster"
    createdBy = "dask-cloudprovider"
  }

  tags_all = {
    cluster   = "hwpc-web-fargate-cluster"
    createdBy = "dask-cloudprovider"
  }

  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs-tasks.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "A role for ECS to use when executing"
  inline_policy {
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/CloudWatchLogsFullAccess", "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceRole", "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"]
  max_session_duration = 3600
  name                 = "hwpc-web-fargate-cluster-execution-role"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "hwpc_web_fargate_cluster_task_role" {
  tags = {
    cluster   = "hwpc-web-fargate-cluster"
    createdBy = "dask-cloudprovider"
  }

  tags_all = {
    cluster   = "hwpc-web-fargate-cluster"
    createdBy = "dask-cloudprovider"
  }

  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ecs-tasks.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "A role for dask tasks to use when executing"
  inline_policy {
  }

  max_session_duration = 3600
  name                 = "hwpc-web-fargate-cluster-task-role"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "read_bucket" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
    name   = "read-hwpc"
    policy = "{\n    \"Version\": \"2012-10-17\",\n    \"Statement\": [\n        {\n            \"Sid\": \"ExampleStmt\",\n            \"Action\": [\n                \"s3:GetObject\"\n            ],\n            \"Effect\": \"Allow\",\n            \"Resource\": [\n                \"arn:aws:s3:::hwpc/*\",\n                \"arn:aws:s3:::hwpc-output/*\"\n            ]\n        }\n    ]\n}"
  }

  managed_policy_arns  = ["arn:aws:iam::aws:policy/AmazonECS_FullAccess", aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2eea173a_6a46_4768_9e63_23b58c209326.id, aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_cf95b68f_f26c_479b_911d_b5afba02d5ed.id]
  max_session_duration = 3600
  name                 = "read-bucket"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.path
}

resource "aws_iam_role" "read_hwpc_bucket" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_9d1c84cf_c232_4998_896f_5dfd1e7a7868.id, aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2e75c241_3019_4862_aae0_2774e918b01e.id]
  max_session_duration = 3600
  name                 = "read-hwpc-bucket"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.path
}

resource "aws_iam_role" "s3_demo_role" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_fc6a086b_8130_486f_8c18_dd0d65011a1c.id, aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.id]
  max_session_duration = 3600
  name                 = "s3_demo_role"
  path                 = "/service-role/"
}

resource "aws_iam_role" "ses_lambda" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  description        = "Allows Lambda functions to call AWS services on your behalf."
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_contact_ses_policy.id]
  max_session_duration = 3600
  name                 = "ses-lambda"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_role" "update_task_dns_role_fh49kuu8" {
  assume_role_policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"lambda.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
  inline_policy {
  }

  managed_policy_arns  = [aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_402dc6ad_e0b0_414e_b565_faf7191fa745.id]
  max_session_duration = 3600
  name                 = "update-task-dns-role-fh49kuu8"
  path                 = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.path
}

resource "aws_iam_role_policy" "aws_quicksetup_stackset_local_administrationrole_assumerole_aws_quicksetup_stackset_local_executionrole" {
  name   = "AssumeRole-AWS-QuickSetup-StackSet-Local-ExecutionRole"
  policy = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Action\":[\"sts:AssumeRole\"],\"Resource\":[\"arn:*:iam::*:role/AWS-QuickSetup-StackSet-Local-ExecutionRole\"],\"Effect\":\"Allow\"}]}"
  role   = "AWS-QuickSetup-StackSet-Local-AdministrationRole"
}

resource "aws_iam_role_policy" "googledrive_lambdaexecutionrole_root" {
  name   = "root"
  policy = "{    \"Version\": \"2012-10-17\",    \"Statement\": [        {            \"Action\": [                \"s3:GetObject\",                \"s3:GetObjectAcl\"            ],            \"Resource\": [                \"arn:aws:s3:::s3-to-google-drive-hwpc/*\",                \"arn:aws:s3:::hwpc-output/*\"            ],            \"Effect\": \"Allow\"        },        {            \"Sid\": \"ListObjectsInBucket\",            \"Effect\": \"Allow\",            \"Action\": \"s3:ListBucket\",            \"Resource\": [                \"arn:aws:s3:::hwpc-output\"            ]        },        {            \"Action\": [                \"ssm:GetParameter\"            ],            \"Resource\": \"arn:aws:ssm:us-west-2:234659567514:parameter/google-*\",            \"Effect\": \"Allow\"        }    ]}"
  role   = "GoogleDrive-LambdaExecutionRole"
}

resource "aws_iam_role_policy" "read_bucket_read_hwpc" {
  name   = "read-hwpc"
  policy = "{    \"Version\": \"2012-10-17\",    \"Statement\": [        {            \"Sid\": \"ExampleStmt\",            \"Action\": [                \"s3:GetObject\"            ],            \"Effect\": \"Allow\",            \"Resource\": [                \"arn:aws:s3:::hwpc/*\",                \"arn:aws:s3:::hwpc-output/*\"            ]        }    ]}"
  role   = "read-bucket"
}

resource "aws_iam_role_policy_attachment" "aws_quicksetup_stackset_local_executionrole_arn_aws_iam__aws_policy_administratoraccess" {
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  role       = aws_iam_role.aws_quicksetup_stackset_local_executionrole.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforamazonssm_arn_aws_iam__aws_policy_aws_service_role_amazonssmservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AmazonSSMServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforamazonssm.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforapplicationautoscaling_ecsservice_arn_aws_iam__aws_policy_aws_service_role_awsapplicationautoscalingecsservicepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSApplicationAutoscalingECSServicePolicy"
  role       = aws_iam_role.awsserviceroleforapplicationautoscaling_ecsservice.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforautoscaling_arn_aws_iam__aws_policy_aws_service_role_autoscalingservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AutoScalingServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforautoscaling.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforcomputeoptimizer_arn_aws_iam__aws_policy_aws_service_role_computeoptimizerservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/ComputeOptimizerServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforcomputeoptimizer.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforecs_arn_aws_iam__aws_policy_aws_service_role_amazonecsservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AmazonECSServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforecs.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforelasticloadbalancing_arn_aws_iam__aws_policy_aws_service_role_awselasticloadbalancingservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSElasticLoadBalancingServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforelasticloadbalancing.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforglobalaccelerator_arn_aws_iam__aws_policy_aws_service_role_awsglobalacceleratorslrpolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSGlobalAcceleratorSLRPolicy"
  role       = aws_iam_role.awsserviceroleforglobalaccelerator.id
}

resource "aws_iam_role_policy_attachment" "awsservicerolefororganizations_arn_aws_iam__aws_policy_aws_service_role_awsorganizationsservicetrustpolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSOrganizationsServiceTrustPolicy"
  role       = aws_iam_role.awsservicerolefororganizations.id
}

resource "aws_iam_role_policy_attachment" "awsservicerolefors3storagelens_arn_aws_iam__aws_policy_aws_service_role_s3storagelensservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/S3StorageLensServiceRolePolicy"
  role       = aws_iam_role.awsservicerolefors3storagelens.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforservicequotas_arn_aws_iam__aws_policy_aws_service_role_servicequotasservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/ServiceQuotasServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforservicequotas.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforsso_arn_aws_iam__aws_policy_aws_service_role_awsssoservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSSSOServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforsso.id
}

resource "aws_iam_role_policy_attachment" "awsserviceroleforsupport_arn_aws_iam__aws_policy_aws_service_role_awssupportservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSSupportServiceRolePolicy"
  role       = aws_iam_role.awsserviceroleforsupport.id
}

resource "aws_iam_role_policy_attachment" "awsservicerolefortrustedadvisor_arn_aws_iam__aws_policy_aws_service_role_awstrustedadvisorservicerolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/aws-service-role/AWSTrustedAdvisorServiceRolePolicy"
  role       = aws_iam_role.awsservicerolefortrustedadvisor.id
}

resource "aws_iam_role_policy_attachment" "cwe_role_us_west_2_frontend_dep_arn_aws_iam__234659567514_policy_service_role_start_pipeline_execution_us_west_2_frontend_dep" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_start_pipeline_execution_us_west_2_frontend_dep.id
  role       = aws_iam_role.cwe_role_us_west_2_frontend_dep.id
}

resource "aws_iam_role_policy_attachment" "ecsautoscalerole_arn_aws_iam__aws_policy_service_role_amazonec2containerserviceautoscalerole" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceAutoscaleRole"
  role       = aws_iam_role.ecsautoscalerole.id
}

resource "aws_iam_role_policy_attachment" "ecstaskexecutionrole_arn_aws_iam__aws_policy_service_role_amazonecstaskexecutionrolepolicy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  role       = aws_iam_role.ecstaskexecutionrole.id
}

resource "aws_iam_role_policy_attachment" "elasticipuserrole_arn_aws_iam__234659567514_policy_elasitcipuserrole" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_elasitcipuserrole.id
  role       = aws_iam_role.elasticipuserrole.id
}

resource "aws_iam_role_policy_attachment" "get_user_json_role_6laoudf0_arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_9da34040_213b_4f9f_bfa0_3a2f368f6731" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_9da34040_213b_4f9f_bfa0_3a2f368f6731.id
  role       = aws_iam_role.get_user_json_role_6laoudf0.id
}

resource "aws_iam_role_policy_attachment" "get_user_json_role_zjiw3n1t_arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_05a402ec_d770_42fe_848a_5e6e6d2574fe" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_05a402ec_d770_42fe_848a_5e6e6d2574fe.id
  role       = aws_iam_role.get_user_json_role_zjiw3n1t.id
}

resource "aws_iam_role_policy_attachment" "googledrive_lambdaexecutionrole_arn_aws_iam__aws_policy_service_role_awslambdabasicexecutionrole" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role_policy.googledrive_lambdaexecutionrole_root.role
}

resource "aws_iam_role_policy_attachment" "hwpc_web_fargate_cluster_execution_role_arn_aws_iam__aws_policy_amazonec2containerregistryreadonly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.hwpc_web_fargate_cluster_execution_role.id
}

resource "aws_iam_role_policy_attachment" "hwpc_web_fargate_cluster_execution_role_arn_aws_iam__aws_policy_cloudwatchlogsfullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
  role       = aws_iam_role.hwpc_web_fargate_cluster_execution_role.id
}

resource "aws_iam_role_policy_attachment" "hwpc_web_fargate_cluster_execution_role_arn_aws_iam__aws_policy_service_role_amazonec2containerservicerole" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceRole"
  role       = aws_iam_role.hwpc_web_fargate_cluster_execution_role.id
}

resource "aws_iam_role_policy_attachment" "read_bucket_arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2eea173a_6a46_4768_9e63_23b58c209326" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2eea173a_6a46_4768_9e63_23b58c209326.id
  role       = aws_iam_role_policy.read_bucket_read_hwpc.role
}

resource "aws_iam_role_policy_attachment" "read_bucket_arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_cf95b68f_f26c_479b_911d_b5afba02d5ed" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_cf95b68f_f26c_479b_911d_b5afba02d5ed.id
  role       = aws_iam_role_policy.read_bucket_read_hwpc.role
}

resource "aws_iam_role_policy_attachment" "read_bucket_arn_aws_iam__aws_policy_amazonecs_fullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
  role       = aws_iam_role_policy.read_bucket_read_hwpc.role
}

resource "aws_iam_role_policy_attachment" "read_hwpc_bucket_arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2e75c241_3019_4862_aae0_2774e918b01e" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_2e75c241_3019_4862_aae0_2774e918b01e.id
  role       = aws_iam_role.read_hwpc_bucket.id
}

resource "aws_iam_role_policy_attachment" "read_hwpc_bucket_arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_9d1c84cf_c232_4998_896f_5dfd1e7a7868" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_9d1c84cf_c232_4998_896f_5dfd1e7a7868.id
  role       = aws_iam_role.read_hwpc_bucket.id
}

resource "aws_iam_role_policy_attachment" "s3_demo_role_arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_accd95e3_9f91_4f08_9ba9_233d317599a4.id
  role       = aws_iam_role.s3_demo_role.id
}

resource "aws_iam_role_policy_attachment" "s3_demo_role_arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_fc6a086b_8130_486f_8c18_dd0d65011a1c" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdas3executionrole_fc6a086b_8130_486f_8c18_dd0d65011a1c.id
  role       = aws_iam_role.s3_demo_role.id
}

resource "aws_iam_role_policy_attachment" "ses_lambda_arn_aws_iam__234659567514_policy_contact_ses_policy" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_contact_ses_policy.id
  role       = aws_iam_role.ses_lambda.id
}

resource "aws_iam_role_policy_attachment" "update_task_dns_role_fh49kuu8_arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_402dc6ad_e0b0_414e_b565_faf7191fa745" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_service_role_awslambdabasicexecutionrole_402dc6ad_e0b0_414e_b565_faf7191fa745.id
  role       = aws_iam_role.update_task_dns_role_fh49kuu8.id
}

resource "aws_iam_user" "administrator" {
  name = "Administrator"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_user" "clairespain" {
  name = "clairespain"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_user" "coltongerth" {
  name = "coltongerth"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_user" "dtuser" {
  name = "dtuser"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_user" "hwpc_sa" {
  name = "hwpc-sa"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_user" "robb" {
  name = "robb"
  path = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.path
}

resource "aws_iam_user_policy_attachment" "clairespain_arn_aws_iam__aws_policy_iamuserchangepassword" {
  policy_arn = "arn:aws:iam::aws:policy/IAMUserChangePassword"
  user       = aws_iam_user.clairespain.id
}

resource "aws_iam_user_policy_attachment" "coltongerth_arn_aws_iam__aws_policy_iamuserchangepassword" {
  policy_arn = "arn:aws:iam::aws:policy/IAMUserChangePassword"
  user       = aws_iam_user.coltongerth.id
}

resource "aws_iam_user_policy_attachment" "dtuser_arn_aws_iam__aws_policy_amazons3fullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  user       = aws_iam_user.dtuser.id
}

resource "aws_iam_user_policy_attachment" "hwpc_sa_arn_aws_iam__234659567514_policy_dask_fargate_policy" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_dask_fargate_policy.id
  user       = aws_iam_user.hwpc_sa.id
}

resource "aws_iam_user_policy_attachment" "hwpc_sa_arn_aws_iam__234659567514_policy_hwpc_sa" {
  policy_arn = aws_iam_policy.arn_aws_iam__234659567514_policy_hwpc_sa.id
  user       = aws_iam_user.hwpc_sa.id
}

resource "aws_iam_user_policy_attachment" "hwpc_sa_arn_aws_iam__aws_policy_amazonec2containerregistryfullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
  user       = aws_iam_user.hwpc_sa.id
}

resource "aws_iam_user_policy_attachment" "hwpc_sa_arn_aws_iam__aws_policy_amazonsesfullaccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
  user       = aws_iam_user.hwpc_sa.id
}

resource "aws_iam_user_policy_attachment" "robb_arn_aws_iam__aws_policy_iamuserchangepassword" {
  policy_arn = "arn:aws:iam::aws:policy/IAMUserChangePassword"
  user       = aws_iam_user.robb.id
}

