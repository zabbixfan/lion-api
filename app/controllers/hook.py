
from flask import jsonify,g,request
from app.models.repo import Repo
from app.common.httpHelp import codeHubRequest as httpHelper
import urllib,json
from app.controllers import ctl
from app.common.EmailOperator import *
from config import Config
from app import celery

def executor(cmd):
    import os, subprocess
    p = subprocess.Popen(['/bin/bash', '-l', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, error = p.communicate()
    return p.communicate()

@celery.task()
def worker(cmds):
    out,error = executor(cmds)
    print out,error


@ctl.route("/githook",methods=['post'])
def hook():
    content = request.json
    print content["event_name"]
    if content["event_name"] == "project_create":
        id = content["project_id"]
        url = Config.GITHOOK_URL
        data={
            "url": url,
            "merge_requests_events": True,
            "push_events": False
        }
        uri = '/api/v4/projects/{}/hooks'.format(id)
        r = httpHelper(uri,data=data,method="post")
    if content["event_name"] == "push" and "checkout_sha" in content.keys():
        if not content["checkout_sha"] is None:
            q = Repo.query.filter(Repo.url == content['project']['git_http_url']).first()
            if q:
                id = urllib.quote_plus(content['project']['path_with_namespace'])
                uri = '/api/v4/projects/{}/repository/files/.gitlab-ci.yml'.format(id)
                params = {
                    'ref': content['ref'].split("/")[-1]
                }
                r = httpHelper(uri=uri, params=params)
                if r.status_code > 300:
                    return "file not found"
                blob = r.json()['blob_id']
                if q.ciBlobId is None:
                    q.ciBlobId=blob
                    q.commit()
                else:
                    if q.ciBlobId != blob:
                        title = 'proejct {} ci file has been changed'.format(content['project']['path_with_namespace'])
                        msg = 'gitlab-ci.yml has been changed when push to {}'.format(content['ref'].split("/")[-1])
                        SendEmail(Config.EMALL_RECEIVERS, title=title, msg=msg, type="text")
                        q.ciBlobId = blob
                        q.commit()

    return "received"

@ctl.route("/gitwebhook",methods=['post'])
def phook():
    print request.data
    content = request.json
    if "object_attributes" in content.keys():
        if content["object_attributes"]["target_branch"].startswith("develop-"):
            if content["object_attributes"]["state"] in ["opened","reopened"]:
                giturl = content["object_attributes"]["source"]["git_http_url"]
                url = '{}sonarrobot:12345678@{}'.format(giturl[0:8],giturl[8:])
                name = content["repository"]["name"]
                branch = content["object_attributes"]["source_branch"]
                id = content["object_attributes"]["source_project_id"]
                iid = content["object_attributes"]["iid"]
                cmd = "cd ~/sonar && rm -rf {path} && git clone {url} && cd {path} && git checkout {branch} && sonar-scanner -Dsonar.projectKey={name} -Dproject.settings=.sonar-project.properties -Dsonar.sources=. -Dsonar.analysis.mergeID={iid} -Dsonar.analysis.projectID={id} -Dsonar.analysis.branch={branch}".format(url=url,name=name,branch=branch,iid=iid,id=id,path=name.lower())
                worker.delay(cmd)
    return "receive"

@ctl.route("/sonarhook",methods=['post'])
def shook():
    content = request.json
    print json.dumps(content,indent=4)
    if "sonar.analysis.mergeID" in content["properties"] and "sonar.analysis.projectID" in content["properties"]:
        reportUrl = "{}/dashboard/index/{}".format(Config.SONAR_URL,content["project"]["name"])
        uri = "/api/v4/projects/{}/merge_requests/{}/notes".format(content["properties"]["sonar.analysis.projectID"],content["properties"]["sonar.analysis.mergeID"])
        status = content["qualityGate"]["status"]
        if status == "OK":
            status = "{{+ {} +}}".format(status)
        else:
            status = "{{- {} -}}".format(status)
        body = "<h1>SonarQuber Result</h1><ul><li>Project: {}</li><li>Source Branch: {}</li><li>SonarQube result: {}</li><li>Detail Url:  {}</li></ul>".format(content["project"]["name"],content["properties"]["sonar.analysis.branch"],status,reportUrl)
        data = {
            "body":body
        }
        r = httpHelper(url=Config.CODEHUB_URL,uri=uri,data=data,method="post")
    return "receive"
