#!codeing:utf-8
import json
from app.common.httpHelp import codeHubRequest
uri = "/api/v4/projects/1/repository/commits/1db155933f168d6f56ce2fe9bf15e88e1f9909e2"
r = codeHubRequest(uri=uri)
#print r.json()["message"]
print json.dumps(r.json(),indent=4)
message = r.json()["message"]
if 'release' in message and 'master' in message and 'Onekit Auto Merge':
    print "true"
else:
    print "false"