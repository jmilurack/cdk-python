import sys
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv,
                          ["param1",
                           "param2",
                           "param3",
                           "param4"])
print (f"The passed in params are: {args}")

print (f"The param1 is: {args['param1']}")
print (f"The param2 is: {args['param2']}")
print (f"The param3 is: {args['param3']}")
print (f"The param4 is: {args['param4']}")
