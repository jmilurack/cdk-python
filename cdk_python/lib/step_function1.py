from aws_cdk import (
    Duration,
    aws_s3 as s3,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_logs as logs,
    aws_lambda as _lambda,
    aws_glue as _glue,
    CfnOutput as _cfn_output,
    Stack,
    aws_s3_assets as _s3_assets,
    aws_iam as _iam
    
)
from constructs import Construct



MAX_CONCURRENCY = 1
STATE_MACHINE_DURATION_MINS = 60
LOG_RETENTION_PERIOD = logs.RetentionDays.ONE_MONTH



class StepFunction1(Construct): 
    '''
    Construct that defines the step function. This example step function
    has 2 steps - a lambda function and a Glue job. There will be a similar
    construct for each step function.
    '''

    def __init__(self, scope: Construct, construct_id: str,  
                 commonStack: Stack, environ: str, **kwargs) -> None:
        super().__init__(scope, construct_id)
            
        logGroup = logs.LogGroup(self, "stepfunction_1", 
                                 retention=LOG_RETENTION_PERIOD,
                                 log_group_name=f"stepfunction-1-{environ}")
        
        lambdaTask = self.create_lambda_task(commonStack, environ)
        glueTask = self.create_glue_job_task(commonStack, environ)
        
        defintion = lambdaTask \
            .next(glueTask) \
            .next(sfn.Succeed(self, "Success"))
        
        sm = sfn.StateMachine(self, "step_function_1", 
                         definition=defintion, 
                         state_machine_type=sfn.StateMachineType.STANDARD,
                         timeout=Duration.minutes(STATE_MACHINE_DURATION_MINS),
                         logs= sfn.LogOptions(destination=logGroup, 
                                              level=sfn.LogLevel.ALL),
                         tracing_enabled=True,
                         state_machine_name=f"stepfunction-1-{environ}"
                         )
            
        _cfn_output(self, "step_function_1_name", value=sm.state_machine_name,
                    description=f"Step function1 name in {environ}",
                    export_name=f"{Stack.of(self).stack_name}::StepFunction1")
        
    def create_lambda_task(self, commonStack: Stack, environ: str) -> tasks.LambdaInvoke:
        lambdaFn = _lambda.Function(self, "lambda-1", 
                                runtime=_lambda.Runtime.PYTHON_3_9,
                                handler="lambda1.handler",
                                vpc=commonStack.vpc,
                                code=_lambda.Code.from_asset("src/lambdas"))
        
        _cfn_output(self, "Lambda_1Name", value=lambdaFn.function_arn,
                    description=f"Lambda1 function name in {environ}",
                    export_name=f"{Stack.of(self).stack_name}::Lambda1")

        commonStack.raw_bucket.grant_read_write(lambdaFn)
        return tasks.LambdaInvoke(self, "lambda_1", 
                                  lambda_function=lambdaFn,
                                  comment="execute pre-etl tasks",
                                  result_path="$.params",
                                  retry_on_service_exceptions=True,
                                  payload_response_only=True)
        
        
        
    def create_glue_job_task(self, commonStack: Stack, environ: str) -> tasks.GlueStartJobRun:

       self.job_1_asset = _s3_assets.Asset(self, "glue-job-1", 
                                    path="src/glue_assets/glue_job_1/glue_job_1_main.py");
       
       self.job_1_asset.grant_read(commonStack.glue_role)

       job_name =  f"glue_job-1-asset-{environ}"
       
       _glue.CfnConnection.PhysicalConnectionRequirementsProperty()
       
       _glue.CfnJob(self, f"glue_job_1_asset",
                                name=job_name,
                                description="Copy glue job script to scripts folder",
                                role=commonStack.glue_role.role_arn,
                                command={
                                    "name": "glueetl",
                                    "pythonVersion": "3",
                                    "scriptLocation": self.job_1_asset.s3_object_url
                                },
                                execution_property={
                                    "maxConcurrentRuns": 150
                                },
                                glue_version="4.0",
                                worker_type="G.1X",
                                number_of_workers=2,
                                timeout=60,
                                max_retries=2,
                                default_arguments={
                                    "--TempDir": f"s3://{self.job_1_asset.s3_bucket_name}/output/temp",
                                    "--job-bookmark-option": "job-bookmark-enable",
                                    "--job-language": "python",
                                    "--spark-event-logs-path": f"s3://{self.job_1_asset.s3_bucket_name}/output/logs",
                                    "--enable-continuous-cloudwatch-log": "true",
                                    "--enable-metrics": "",
                                    "--enable-spark-ui": True,
                                    "--disable-proxy-v2": True
                                },
                                connections= \
                                  _glue.CfnJob.ConnectionsListProperty(
                                      connections=[commonStack.glue_network_connection.connection_input.name])
       )
        
       glueJobTask = tasks.GlueStartJobRun(self, "glue_job_1", 
                                        glue_job_name=job_name,
                                        input_path="$.params",
                                        integration_pattern=sfn.IntegrationPattern.RUN_JOB,
                                        arguments=sfn.TaskInput.from_object({
                                            "--param1": sfn.JsonPath.string_at("$.param1"),
                                            "--param2": sfn.JsonPath.string_at("$.param2"),
                                            "--param3": sfn.JsonPath.string_at("$.param3"),
                                            "--param4": sfn.JsonPath.string_at("$.param4")
                                        })
                                        )           
       return glueJobTask