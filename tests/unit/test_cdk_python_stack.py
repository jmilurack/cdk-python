import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_python.step_functions_stack import StepFunctionsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_python/cdk_python_stack.py
def test_stepfunctions_created():
    app = core.App()
    stack = StepFunctionsStack(app, "stepfunctions-test")
    template = assertions.Template.from_stack(stack)

    print(template.to_json)
    #template.has_resource_properties("AWS::SQS::Queue", {
    #     "VisibilityTimeout": 300
    # })
