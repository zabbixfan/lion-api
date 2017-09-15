from flask_restful import Resource,reqparse,inputs
from flask import jsonify,g,request,abort,render_template
import json,requests,time
from ..common.alopex_auth_sdk import need_login2
from app.controllers import ctl
from app.common.httpHelp import codeHubRequest as http_helper
from app.domain.branch import Branches
from app import logger,cache
from werkzeug.contrib.cache import SimpleCache
from config import Config
@ctl.route("/project",methods=['get'])
def projectList():
    uri = "/api/v4/groups"
    r = http_helper(uri=uri)
    list = r.json()
    # list =[namespace for namespace in r.json() if namespace["kind"]=="group"]
    # uri = "/api/v4/groups"
    # r = http_helper(uri=uri)
    # print json.dumps(r.json(),indent=4)
    # print list
    # for a in list:
    #     print a["id"],a["name"]
    a = render_template("index.html",list=list)
    # print a
    return render_template("index.html",list=list)

@ctl.route("/project",methods=['post'])
def createProject():
    rq=reqparse.RequestParser()
    rq.add_argument("url")
    rq.add_argument("namespace")
    rq.add_argument("user[]",dest="user",action="append")
    args=rq.parse_args()
    errors = False

    # import project
    uri = '/api/v4/projects'
    name = args.url.split("/")[-1].replace(".git","")
    import_url = '{}songcheng3215:Sc10275858@{}'.format(args.url[0:7], args.url[7:])
    data = {
        "name": name,
        "namespace_id": args.namespace,
        "visibility": "internal",
        "import_url": import_url
    }
    r = http_helper(uri=uri,method="post",data=data)
    if r.status_code < 300:

        # protect branch
        id = r.json()["id"]
        url = r.json()["http_url_to_repo"]

        #update cmdb
        res = updateCMDBinfo(args.url, url)
        while True:
            uri = '/api/v4/projects/{}'.format(id)
            r = http_helper(uri=uri, method="get")
            b = r.json()["default_branch"]
            if not b is None:
                break
        uri = '/api/v4/projects/{}/repository/branches/master/protect'.format(id)
        r = http_helper(uri=uri, method="put")
        if r.status_code < 300:
            print "create repo success"

            # add user to group
            if args.user:
                userId = getUserId(args.user)
                for id in userId:
                    uri = '/api/v4/groups/{}/members'.format(args.namespace)
                    data = {
                        "user_id": id,
                        "access_level": 30
                    }
                    r = http_helper(uri=uri,data=data,method="post")
                    if r.status_code < 300:
                        print "add user ok"
                    else:
                        # errors = True
                        print "{}:{}".format(id,r.content)
        else:
            errors = True
            print r.content
            rs = r.content
    else:
        errors = True
        print r.content
        rs = r.content
    if not errors:
        if res is None:
            return jsonify({"r": 1, "rs": "create project success"}), 200
        return jsonify({"r":1,"rs":"create project success,but {},new_url is {}".format(res["data"],url)}),200
    else:
        return jsonify({"r":2,"rs":rs}),404
    return "123123"
def getUserId(username):
    current = 1
    total = 1
    pageSize = 100
    userid = []
    while current <= total:
        uri = '/api/v4/users?per_page={}&page={}'.format(pageSize, current)
        result = http_helper(uri=uri, method="get")
        total = int(result.headers['X-Total-Pages'])
        current += 1
        userid.extend([user["id"] for user in result.json() if user["username"] in username])
    # userid = [user["id"] for user in result.json() if user["username"] in username ]
    print userid
    return userid
@ctl.route("/user/<id>",methods=["get"])
def a(id):
    # uri = '/api/v4/projects/{}'.format(id)
    uri = '/api/v4/users/{}'.format(id)
    r = http_helper(uri=uri, method="get")
    print json.dumps(r.json(), indent=4)
    return jsonify(r.json())

def updateCMDBinfo(import_url,url):
    new_repo = url
    projects = cache.get("p")
    url = Config.CMDB_URL
    if projects is None:
        print "not cached"
        uri = "/api/projects"
        projects = http_helper(url=url,uri=uri).json()
        cache.set("p",projects,timeout=5*60)
    for p in projects["data"]:

        if p["repo"]==import_url:
            uri = "/api/project/{}".format(p["id"])
            result = http_helper(uri=uri,url=url).json()["data"]
            data = {
                "name": result["name"],
                "groupId": result["group"]["id"],
                "describe": result["describe"],
                "repoUrl": new_repo,
                "projectType": result["projectType"],
                "manager": result["manager"]
            }
            result = http_helper(uri=uri,url=url,data=data,method="put").json()["data"]
            break
    else:
        result = {
            "data":"import_url not found on cmdb,please check"
        }

    return result


@ctl.route("/cmdb/project",methods=["post"])
def b():
    # repo = request.json["repo"]
    # new_repo = request.json["new"]
    projects = cache.get("p")
    url = Config.CMDB_URL
    data = []
    if projects is None:
        print "not cached"
        uri = "/api/projects"
        projects = http_helper(url=url,uri=uri).json()
        cache.set("p",projects,timeout=5*60)
        data = [p for p in projects['data'] if p['repo'].startswith("http://gitlab.apitops.com")]
    # for p in projects["data"]:
    #     if p["repo"]==repo:
    #         uri = "/api/project/{}".format(p["id"])
    #         result = http_helper(uri=uri,url=url).json()["data"]
    #         data = {
    #             "name": result["name"],
    #             "groupId": result["group"]["id"],
    #             "describe": result["describe"],
    #             "repoUrl": new_repo,
    #             "projectType": result["projectType"],
    #             "manager": result["manager"]
    #         }
    #         result = http_helper(uri=uri,url=url,data=data,method="put").json()["data"]
    #         break
    # else:
    #     result = {
    #         "data":"import_url not found on cmdb,please check"
    #     }

    return jsonify({'data':data})
@ctl.route("/cmdb/project/<id>",methods=["get","post"])
def c(id):
    url = Config.CMDB_URL
    uri = "/api/project/{}".format(id)
    print request.method


    # uri = "/api/select/projectgroups"
    result = http_helper(url=url,uri=uri)
    return jsonify(result.json())
