from app import db
from ..common.time_helper import timestamp_to_datetime
from uuid import uuid1 as uuid
class Repo(db.Model):
    __tablename__='pacific_repo'
    repoId = db.Column(db.String(32), primary_key=True)
    url = db.Column(db.String(255), default="")
    name = db.Column(db.String(255), default="")
    owner = db.Column(db.String(255), default="")
    path = db.Column(db.String(255), default="")
    createAt = db.Column(db.DATETIME, default=timestamp_to_datetime(0))
    lastActivityAt = db.Column(db.DATETIME, default=timestamp_to_datetime(0))
    isSync = db.Column(db.Integer,default=0)
    lastPushMaster = db.Column(db.String(255),default="")
    ciBlobId = db.Column(db.String(255),default="")
    def save(self,wait_commit=False):
        if not self.repoId:
            self.repoId=uuid().get_hex()
        db.session.add(self)
        if wait_commit:
            db.session.flush()
        else:
            db.session.commit()
    @staticmethod
    def commit():
        db.session.commit()