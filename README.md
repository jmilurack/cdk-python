
# Welcome to your CDK Step Function template

This is an example of creating an ETL pipeline using AWS step functions,
AWS Glue and CDK (Python) for deployment

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

Set the environment parameters in cdk.json:

```json
    "dev": {
      "account": "817409382164",
      "region": "us-east-1",
      "vpcId": "vpc-038189879b314a673", 
      "glueSecurityGroups": ["sg-0e25604157f580f62", "sg-0d0a26928961bffaa", "sg-0e66bc52113add52e"],
      "eventBus": "arn:aws:events:us-east-1:817409382164:event-bus/default"
    }
```
The default lifecycle is set in the file `app.python` on line 13 (dev). You can override it as a context variable to the cdk cli.
## Available CloudFormation stacks:

* `CommonStack`   Creates all AWS resources that are needed by the application,
    i.e. S3 buclets, roles, connections, etc
* `StepFunctionsStack`   Creates the application. In this case the application consists of 
    a single step function, but there could be more


## Useful commands for inrastructure depoyment.

* `cdk deploy stackname`      deploy this stack to your default AWS account/region
* `cdk diff`                  compare deployed stack with current state
* `cdk synth`                 emits the synthesized CloudFormation template
* `cdk ls`          list all stacks in the app
* `cdk docs`        open CDK documentation

## Setup Instructions (to run under the root project folder):

* clone this repository locally
* download and install Python, pip an virtualenv
* `python3 -m ensurepip --upgrade`            
* `python3 -m pip install --upgrade pip`        
* `python3 -m pip install --upgrade virtualenv` 
* `cdk ls`                                

## To run one single TypeScript file:

* `cdk deploy your-stack-name`       to deploy a CloudFormation stack in AWS

## Environmental parameters description:
###### account
The ID of the AWS account where the stacks will be deployed
###### region
The AWS region where the stacks will be deployed
###### vpcId
The AWS VPC where the resources will be deployed. It is passed in because the VPC is pre-existing. The `CommonStack` is using this parameter to lookup the VPC, which is then used by the remaining constructs.
###### glueSecurityGroups
A list of VPC security groups, which will be used for the network connection in AWS Glue
###### eventBus
The ARN of the eventbus that will be used by the application
