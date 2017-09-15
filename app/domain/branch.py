from app.common.httpHelp import codeHubRequest as http_helper
import urllib,json,time
from config import Config
from app import logger
from app.common.alopex_auth_sdk import need_sign
class Branches:
    def __init__(self,git):
        self.git = git
        self.id=self.getid()
        self.uri = '/api/v4/projects/{}/repository/branches'.format(self.id)
    def getid(self):
        project = self.git.replace(".git","").split("/")[-1]
        namespace = self.git.split("/")[-2]
        encoded = urllib.quote_plus('{}/{}'.format(namespace, project))
        return encoded
    @property
    def branchList(self):
        current = 1
        total = 1
        pageSize = 100
        data = []
        while current <= total:
            uri = '{}?per_page={}&page={}'.format(self.uri,pageSize, current)
            r = http_helper(uri)
            total = int(r.headers['X-Total-Pages'])
            current += 1
            if r.status_code > 300:
                return {
                    'message': 'error',
                    'data': str(r.json()['message'])
                }
            for branch in r.json():
                data.append({
                    'name': str(branch['name']),
                    'protect': str(branch['protected']),
                    'committer_name': str(branch['commit']['committer_name']),
                    'committed_date': str(branch['commit']['committed_date']),
                })
        return {
            'message': 'ok',
            'data': data
        }
    @need_sign()
    def create(self,name,ref,protect):
        data = {
            'branch': name,
            'ref': ref
        }
        r = http_helper(uri=self.uri,method='post',data=data)

        if r.status_code > 300:
            logger().info('create failed:{},git:{},name:{},ref:{}'.format(r.content,self.git,name,ref))
            return {
                'message': 'error',
                'data': str(r.json().values()[0])
            }
        if protect:
            self.protect(name)
        if not self.getDefault().startswith("develop"):
            self.setDefault(name)
        return {
            'message': 'ok',
            'data': 'create new branch {} success'.format(name)
        }
    @need_sign()
    def delete(self,name):
        nameList = [b for b in self.branchList['data']]
        if self.getDefault() == name:
            names = [b["name"] for b in nameList if b["name"]!= name and b["name"].startswith("develop")]
            if names:
                names.sort()
                n = names[0]
            elif "master" in [b["name"] for b in nameList]:
                n = "master"
            else:
                n = [b["name"] for b in nameList][0]
            self.setDefault(name=n)
        for b in nameList:
            if b['name'] == name and b['protect'] == "True":
                self.protect(name,release=True)

        uri = '{}/{}'.format(self.uri,name)
        r = http_helper(uri=uri,method='delete')
        if r.status_code > 300:
            logger().info('delete {} failed:{}'.format(name,r.content))
            return {
                'message': 'error',
                'data': str(r.json()['message'])
            }
        return {
            'message': 'ok',
            'data': 'delete branch {} success'.format(name)
        }
    def protect(self,name,release=False):
        data = {
            "developers_can_merge":True
        }
        uri = '{}/{}/protect'.format(self.uri, name)
        if release is True:
            uri = '{}/{}/unprotect'.format(self.uri, name)
        r = http_helper(uri=uri,method='put',data=data)
        if r.status_code > 300:
            logger().info('protect/unprotect {} failed:{}'.format(name,r.content))
            return {
                'message': 'error',
                'data': str(r.json()['message'])
            }
        return {
            'message': 'ok',
            'data': 'protect/unprotect branch {} success'.format(name)
        }
    def merge(self,name,target,title):
        uri = '/api/v4/projects/{}/merge_requests?state=opened'.format(self.id)
        r = http_helper(uri=uri)
        if r.status_code > 300:
            return {
                'message': 'error',
                'data': str(r.json()['message'])
            }

        for mr in r.json():
            if mr['source_branch']==name and mr['target_branch'] == target:
                uri = '/api/v4/projects/{}/merge_requests/{}'.format(self.id,mr['iid'])
                r = http_helper(uri=uri,method='delete')
                if r.status_code > 300:
                    return {
                        'message': 'error',
                        'data': r.content
                    }
        branch = self.branchList['data']
        sub = set([name,target])
        main =set([b['name'] for b in branch])
        if not sub.issubset(main):
            return {
                'message': 'error',
                'data': '{} or {} not in branchs'.format(name,target)
            }
        uri = '/api/v4/projects/{}/merge_requests'.format(self.id)
        data = {
            'source_branch':name,
            'target_branch':target,
            'title':title
        }
        r = http_helper(uri=uri,method='post',data=data)

        if r.status_code < 300:
            return self.mergeById(r.json()['iid'])
        else:
            logger().info('create merge failed:{}'.format(r.content))
            return {
                'message': 'error',
                'data': str(r.json()['message'])
            }
    def getDefault(self):
        uri = '/api/v4/projects/{}'.format(self.id)
        default = http_helper(uri=uri).json()["default_branch"]
        return default
    def setDefault(self,name):
        uri = '/api/v4/projects/{}'.format(self.id)
        data = {
            "default_branch":name
        }
        r = http_helper(uri=uri,data=data,method="put")
        # print json.dumps(r.json(),indent=4)
        return "ok"

    def mergeById(self,mid):
        uri = '/api/v4/projects/{}/merge_requests/{}/merge'.format(self.id, mid)
        r = http_helper(uri=uri, method='put')
        if r.status_code == 200:
            return {
                'message': 'ok',
                'data': 'merge by mid {} success'.format(mid)
            }
        else:
            logger().info('merge {} failed:{},git:{}'.format(mid, r.content,self.git))
            return {
                'message': 'error',
                'data': str(r.json()['message'])
            }
    def mergelist(self):
        uri = '/api/v4/projects/{}/merge_requests?state=opened'.format(self.id)
        r = http_helper(uri=uri)
        if r.status_code > 299:
            return {
                'message': 'error',
                'data': str(r.json()['message'])
            }
        return {'messgae': 'ok',
                'data':[{'source':mr['source_branch'],'target':mr['target_branch'],'mid':mr['iid'],'status':mr['merge_status']} for mr in r.json()]
                }


def getGitById(pid):
    url = Config.CMDB_URL
    uri = '/api/project/{}'.format(pid)
    r = http_helper(uri=uri,url=url)
    if not r.json()['data'] is None:
        if len(r.json()['data']['repoUrl'])>0:
            git = r.json()['data']['repoUrl']
        else:
            git = 'http://gitlab.apitops.com/bbb/cc.git'
    else:
        git = 'http://gitlab.apitops.com/bbb/cc.git'
    return git


def branchList(pid):
    git = getGitById(pid)
    b=Branches(git)
    return b.branchList

def namespace():
    uri = "/api/v4/namespaces"
    r = http_helper(uri=uri)
    print json.dumps(r.json(),indent=4)

