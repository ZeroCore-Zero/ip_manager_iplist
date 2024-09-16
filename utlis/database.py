from .app import db


class DeviceInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    HostName = db.Column(db.String(255), nullable=False)
    MAC = db.Column(db.String(255))
    IAID = db.Column(db.String(255))
    IPv4 = db.Column(db.String(255))
    IPv6 = db.Column(db.String(255))
    IPv4_DUID = db.Column(db.String(255))
    IPv6_DUID = db.Column(db.String(255))
    IPv4_OutTime = db.Column(db.Integer)
    IPv6_OutTime = db.Column(db.Integer)
    OnlineTime = db.Column(db.Interval)
    isLogged = db.Column(db.Boolean, default=False)
