#!/usr/bin/python
import argparse,os,subprocess,shutil

app = {
    "organization":{
        "dest": "organization",
        "build": "gulp publish --",
        "node_dir": "top.sass.web-organization"
    },
    "admin":{
        "dest": "",
        "build": "gulp publish --",
        "node_dir": "top.sass.web-admin"
    }
}


parser = argparse.ArgumentParser()
parser.add_argument("-d --dir",help="which dir want to package",dest="dir",nargs="+",required=True)
parser.add_argument("-v --verison",help="ci version",dest="version",required=True)
parser.add_argument("-n --env",help="which environment want to package",dest="env",nargs="+",required=True,choices=("test","dev","beta","v5"))
parser.add_argument("-p --project",help="which project want to package",dest="project",required=True)
parser.add_argument("--publish",help="auto publish",dest="publish",default=False)
args = parser.parse_args()

def colorfulScript(cmd):
    return "\033[1;32;40m{}\033[0m".format(cmd)


def excute(cmd):
    p = subprocess.Popen(['/bin/bash', '-l', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    if err:
        raise Exception, colorfulScript(err)
    return out
def osexcute(cmd):
    status = os.system(cmd)
    if status != 0:
        raise Exception,"command error"

dirs = args.dir
for env in args.env:
    dest = "{}_dist".format(args.project)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    print colorfulScript("mkdir {}".format(dest))
    os.mkdir(dest)
    for dir in dirs:
        if os.path.isdir(dir):
            if dir in app.keys():
                print colorfulScript("cd {}".format(dir))
                os.chdir(dir)
                # start buffer
                buffer_cmd = "mkdir -p ~/modules/{node_dir}/node_modules && test -d node_modules || ln -s ~/modules/{node_dir}/node_modules node_modules".format(node_dir=app[dir]["node_dir"])
                print colorfulScript(buffer_cmd)
                print excute(buffer_cmd)

                yarn_cmd = "yarn install"
                print colorfulScript(yarn_cmd)
                osexcute(yarn_cmd)

                # start build
                build_cmd = "{}{}".format(app[dir]["build"],env)
                print colorfulScript(build_cmd)
                osexcute(build_cmd)
                if dir == "admin":
                    mv_cmd = "mv dist/* ../{}".format(dest)
                else:
                    mv_cmd = "mv dist  ../{}/{}".format(dest,app[dir]["dest"])
                print colorfulScript(mv_cmd)
                print excute(mv_cmd)


                print colorfulScript("cd ..")
                os.chdir(os.path.dirname(os.getcwd()))

            else:
                raise Exception, "app not config for {}".format(dir)
        else:
            raise Exception, "dir {} not found".format(dir)
    # start package
    package_cmd = "tar czvf {}.tar.gz  -C {}/ .".format(args.project,dest)
    print colorfulScript(package_cmd)
    osexcute(package_cmd)
    # start upload
    upload_cmd = "uploadPackage.py -p {project} -n {env} -v {version} -g {project}.tar.gz --publish {publish}".format(project=args.project,version=args.version,publish=args.publish,env=env)
    print colorfulScript(upload_cmd)
    print excute(upload_cmd)