from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_s3 as _s3,
    aws_iam as _iam,
    CfnOutput as _cfn_output,
    aws_ec2 as _ec2,
    aws_glue as _glue,
    aws_stepfunctions as sfn
)
from constructs import Construct

class CommonStack(Stack):
    '''
    Creates all AWS resources that are needed by the application,
    i.e. S3 buclets, roles, connections, etc.
     
    '''
    def __init__(self, scope: Construct, construct_id: str,
                 environ: str, 
                 vpc_id: str, 
                 glue_security_groups: list,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        self.raw_bucket = self.create_landing_bucket(environ, **kwargs)    
        self.glue_role = self.create_glue_job(environ=environ, **kwargs)
        self.vpc = _ec2.Vpc.from_lookup(self, f"vpc_{environ}", vpc_id=vpc_id)
        self.raw_bucket.grant_read_write(self.glue_role)
        
        self.glue_network_connection = self.create_glue_vpc_connection(environ, 
                                                                       glue_security_groups, 
                                                                       **kwargs)
        _cfn_output(self, "rawbucket_arn", value=self.raw_bucket.bucket_arn,
                    description=f"Raw bucket arn in {environ}",
                    export_name=f"{Stack.of(self).stack_name}::RawBucketArn")

        _cfn_output(self, "glue_role", value=self.glue_role.role_arn,
                    description=f"Glue job role used for ETL in {environ}",
                    export_name=f"{Stack.of(self).stack_name}::ETLGlueJobRoleArn")
        
    def create_landing_bucket(self, environ: str, **kwargs) -> _s3.Bucket:
        return _s3.Bucket(self, "etl-migration-storage",
                         bucket_name=f"etl-migration-storage-{environ}", 
                         auto_delete_objects=False if environ == "prod" else True,
                         removal_policy=RemovalPolicy.RETAIN if environ == "prod" else RemovalPolicy.DESTROY,
                         encryption=_s3.BucketEncryption.KMS,
                         block_public_access=_s3.BlockPublicAccess.BLOCK_ALL,
                         enforce_ssl=True,
                         lifecycle_rules=[
                            _s3.LifecycleRule(
                                abort_incomplete_multipart_upload_after=Duration.days(30),
                                expiration=Duration.days(90))
                            ]
                  )
    def create_glue_job(self, environ: str, **kwargs) -> _iam.Role :
       glue_role = _iam.Role(self, f"glue-role-{environ}",
                            role_name=f"aws-glue-migtationrole-{environ}",
                            description="Assign all needed permissions to ETL jobs",
                            managed_policies=[
                            _iam.ManagedPolicy.from_managed_policy_arn(self, "glue-service-policy", "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"),   
                            ],
                            assumed_by=_iam.ServicePrincipal("glue.amazonaws.com")
       )
       return glue_role

    def  create_glue_vpc_connection(self, environ: str,
                                    glue_security_groups: str, 
                                    **kwargs) -> _glue.CfnConnection:
       physical_connection_reqs = \
        _glue.CfnConnection.PhysicalConnectionRequirementsProperty(availability_zone=self.vpc.availability_zones[0],
                                                                   security_group_id_list=glue_security_groups,
                                                                   subnet_id=
                                                                    self.vpc.private_subnets[0] \
                                                                                    .subnet_id
                                                                  )
       connection_input = _glue.CfnConnection.ConnectionInputProperty(
           connection_type="NETWORK",
           description="network connection so that Glue jobs can have access to VPC resources",
           name= f"glue-network-{environ}",
           physical_connection_requirements=physical_connection_reqs
           
       )
           
       
       network = _glue.CfnConnection(self, f"vpc_connection_{environ}", 
                                     catalog_id=Stack.of(self).account,
                                     connection_input= connection_input
                                     )
       return network
