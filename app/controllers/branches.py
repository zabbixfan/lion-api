from flask_restful import Resource,reqparse,inputs
from flask import jsonify,g,request,abort,make_response
import json,requests,time
from . import api
from ..common.alopex_auth_sdk import need_login2
from ..domain.branch import branchList,Branches,getGitById,namespace

from app.controllers import ctl
from app import logger

def post_args():
    rp=reqparse.RequestParser()
    rp.add_argument('name',required=True)
    rp.add_argument('ref',type=unicode,required=False, nullable=False)
    rp.add_argument('target', type=unicode, required=False, nullable=False)
    rp.add_argument('pid',required=True)
    rp.add_argument('protect', type=bool,default=False)
    rp.add_argument('release', type=bool, default=False)
    rp.add_argument('mid',type=int)
    rp.add_argument('title')
    return rp.parse_args()

def get_args():
    rp=reqparse.RequestParser()
    rp.add_argument('name',type=unicode)
    rp.add_argument('pid',type=unicode,required=True)
    rp.add_argument('release',type=unicode,default=False)
    return rp.parse_args()



class branches(Resource):
    def get(self):
        '''
        
        Get All Branches
        ---
        parameters:
          - in: "query"
            name: pid
            required: true
            type: integer
        tags: 
            - branches
        '''
        args=get_args()
        return jsonify(branchList(args.pid))

api.add_resource(branches,'/branches')

@ctl.route("/branch/protected",methods=['post'])
def protect():
    '''

    protect the specified branch
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
        name: release
        required: false
        type: boolen
    tags: 
        - branch
    '''
    args=post_args()
    git = getGitById(args.pid)
    b=Branches(git)

    return jsonify(b.protect(args.name,args.release))

@ctl.route("/branch/create",methods=['post'])
def create():
    '''

    create new branch from ref
    ---
    parameters:
      - in: json
        name: pid
        required: true
        type: integer
      - in: json
        name: name
        required: true
        type: string
      - in: json
        name: ref
        required: true
        type: string
      - in: json
        name: protect
        required: true
        type: boolean
        default: false
    tags: 
        - branch
    '''
    args=post_args()
    git = getGitById(args.pid)
    b = Branches(git)
    return jsonify(b.create(args.name,args.ref,args.protect))

@ctl.route("/branch/delete",methods=['post'])
def delete():
    '''

    delete the specified branch
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
        - branch
    '''
    args = post_args()
    git = getGitById(args.pid)
    b = Branches(git)

    return jsonify(b.delete(args.name))

@ctl.route("/branch/merge",methods=['post'])
def merge():
    '''

    merge the specified branch to target branch
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
        name: target
        required: true
        type: string
      - in: "json"
        name: title
        required: true
        type: string
    tags: 
        - branch
    '''
    args = post_args()
    git = getGitById(args.pid)
    b = Branches(git)
    return jsonify(b.merge(args.name,args.target,args.title))

@ctl.route("/mrlist/<pid>",methods=['get'])
def mergeList(pid):
    '''

    list all specified project merge request
    ---
    tags: 
        - branch
    '''
    git = getGitById(pid)
    b = Branches(git)

    return jsonify(b.mergelist())

@ctl.route("/branch/mr",methods=['post'])
def mergebyid():
    '''

    merge request by mid
    ---
    parameters:
      - in: "json"
        name: pid
        required: true
        type: integer
      - in: "json"
        name: mid
        required: true
        type: string
    tags: 
        - branch
    '''
    rq = reqparse.RequestParser()
    rq.add_argument("mid",type=int)
    rq.add_argument("pid", type=int)
    args=rq.parse_args()
    git = getGitById(args.pid)
    b = Branches(git)
    return jsonify(b.mergeById(args.mid))

