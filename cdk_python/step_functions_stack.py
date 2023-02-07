from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    aws_stepfunctions as sfn
)
from constructs import Construct

from cdk_python.lib.step_function1 import StepFunction1

class StepFunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 commonStack: Stack, environ: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        StepFunction1(self, construct_id=construct_id, commonStack=commonStack, 
                      environ=environ, **kwargs)
        