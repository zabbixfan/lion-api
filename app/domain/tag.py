from app.common.httpHelp import codeHubRequest as http_helper
import urllib,json,time
from config import Config
from app import logger
from app.common.alopex_auth_sdk import need_sign
from app.domain.branch import getGitById,Branches

def create(git,name,ref,message,release):
    b=Branches(git)
    id = b.getid()
    uri = "/api/v4/projects/{}/repository/tags".format(id)
    data = {
        'tag_name': name,
        'ref': ref,
        'message': message,
        'release_description': release
    }
    r=http_helper(uri=uri,data=data,method="post")
    if r.status_code > 299:
        return {
                'message': 'error',
                'data': r.json()['message']
            }
    else:
        return {
            'messgae':'ok',
            'data': 'create tag {} success'.format(name)
        }
def delete(git,name):
    b=Branches(git)
    id = b.getid()
    uri = "/api/v4/projects/{}/repository/tags/{}".format(id,name)
    r=http_helper(uri=uri,method="delete")
    if r.status_code > 299:
        return {
                'message': 'error',
                'data': r.json()['message']
            }
    else:
        return {
            'messgae':'ok',
            'data': 'delete tag {} success'.format(name)
        }