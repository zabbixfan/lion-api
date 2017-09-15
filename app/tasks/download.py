import paramiko,os,logging
remotedir = '/out/'
localdir = '/opt/nkberfile/'
hostname = '114.80.87.49'
port = 22
user = 'JRCJ_XG_STG5'
passd = 'JRCJ_XG@STG5'
logfile = '/home/manatee/file.log'
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',filename='file.log',filemode='a')

class Files:
    def __init__(self,ip,username,passd,timeout=30):
        self.ip = ip
        self.username = username
        self.passd = passd
        self.timeout = timeout
    def sftp_get(self,remotedir,localdir):
        try:
            t= paramiko.Transport((self.ip,22))
            t.connect(username=self.username,password=self.passd)
            sftp = paramiko.SFTPClient.from_transport(t)
            remote = sftp.listdir(remotedir)
            local = os.listdir(localdir)
            for file in remote:
                if file not in local and file.endswith(".zip"):
                    logging.info("put {}{}".format(remotedir, file))
                    sftp.get(os.path.join(remotedir, file), os.path.join(localdir, file))
            t.close()
        except Exception,e:
            logging.error(e)
f=Files(hostname,user,passd)
f.sftp_get(remotedir,localdir)