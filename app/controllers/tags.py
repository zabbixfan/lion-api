from flask_restful import Resource,reqparse,inputs
from flask import jsonify,request
import json,requests,time
from ..common.alopex_auth_sdk import need_login2
from ..domain.branch import getGitById
from app.domain.tag import create,delete
from app.controllers import ctl

@ctl.route("/tag/create",methods=['post'])
def create_tag():
    '''

    Creates a new tag in the repository that points to the supplied ref.
    ---
    parameters:
      - in: "json"
        name: pid
        required: true
        type: integer
      - in: "json"
        name: name
        required: true
        type: string
      - in: "json"
        name: ref
        required: true
        type: string
      - in: "json"
        name: message
        required: false
        type: string
      - in: "json"
        name: release
        required: false
        type: string
    tags: 
        - tag
    '''

    rq = reqparse.RequestParser()
    rq.add_argument("pid",type=int,required=True)
    rq.add_argument("name",required=True,type=unicode)
    rq.add_argument("ref",required=True,type=unicode)
    rq.add_argument("message", required=False,default="")
    rq.add_argument("release", required=False,default="")

    args=rq.parse_args()

    git = getGitById(args.pid)
    # if "message" not in args.keys():
    #     args.message = ""
    return jsonify(create(git,args.name,args.ref,args.message,args.release))


@ctl.route("/tag/delete",methods=['post'])
def delete_tag():
    '''

    Delete a specified tag 
    ---
    parameters:
      - in: "json"
        name: pid
        required: true
        type: integer
      - in: "json"
        name: name
        required: true
        type: string

    tags: 
        - tag
    '''

    rq = reqparse.RequestParser()
    rq.add_argument("pid",type=int,required=True)
    rq.add_argument("name",required=True,type=unicode)
    args=rq.parse_args()
    git = getGitById(args.pid)
    return jsonify(delete(git,args.name))