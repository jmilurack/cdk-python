from aws_cdk import App
import json
import os

def get_context_param(stage: str, key: str) : 
    '''
    This function is used to retrieve variable from the CDK context
    If the ley cannot be found, returns None
        Parameters:
            stage (str): One of dev, stage, prod
            key (str): the key to lookup the value
    
    '''
    print(os.getcwd())
    with open("cdk.json") as f:
        _context = json.load(f)
    app = App(context=_context["context"])   
    env = app.node.try_get_context(stage)
    return env.get(key, None)
    