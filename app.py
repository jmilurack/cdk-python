#!/usr/bin/env python3
import os

import aws_cdk as cdk
import src.common as cmn

from cdk_python.common_stack import CommonStack
from cdk_python.step_functions_stack import StepFunctionsStack

cdkStack = []
app = cdk.App()

DEFAULT_ENVIRON = "dev"
_env = app.node.try_get_context("env")
env = DEFAULT_ENVIRON if _env == None else _env

awsEnv = cdk.Environment(account=cmn.get_context_param(env, "account"),
                         region=cmn.get_context_param(env, "region"))

commonStack = CommonStack(app, "CommonStack", env=awsEnv, environ=env,
                          vpc_id=cmn.get_context_param(env, "vpcId"),
                          glue_security_groups=cmn.get_context_param(env, "glueSecurityGroups"))




stepFunctionsStack = StepFunctionsStack(app, "StepFunctionsStack", env=awsEnv, 
                                        commonStack=commonStack, environ=env)

cdkStack.append(commonStack)
cdkStack.append(stepFunctionsStack)

for stack in cdkStack:
    cdk.Tags.of(stack).add("Application", "app_name", priority=300 )
    cdk.Tags.of(stack).add("CreatedBy", "CDK", priority=300 )
    cdk.Tags.of(stack).add("Stage", env, priority=300 )
    cdk.Tags.of(stack).add("Owner", "CompanyName", priority=300 )
app.synth()
