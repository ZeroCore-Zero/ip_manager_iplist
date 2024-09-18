from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


from .config import Config
from .authentication import isLogged


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)


from .database import DeviceInfo


def class_to_json(device: DeviceInfo):
    data = {
        "hostname": device.HostName,
        "mac": device.MAC,
        "iaid": device.IAID,
        "duid": device.IPv4_DUID,  # 特例
        "ipv4": device.IPv4,
        "ipv6": device.IPv6,
        "dhcp_expiry": device.IPv4_OutTime,  # 特例
        "onlinesecs": device.OnlineTime.total_seconds(),
        "logged_in": isLogged(device.IPv4)  # 临时解决，没想到有什么监听用户登录请求的其他方法（除了抓包）
        # "logged_in": device.isLogged if device.isLogged is not None else isLogged(device.IPv4)
    }
    check_list = [
        "duid", "mac", "iaid",
        "ipv4", "ipv6", "logged_in"
    ]
    for key in check_list:
        if data[key] is None or (isinstance(data, str) and len(data[key]) == 0):
            data.pop(key)
    return data


@app.route('/all_devices', methods=['GET'])
def get_all_devices():
    devices = DeviceInfo.query.order_by(DeviceInfo.HostName).all()
    return jsonify({
        "status": "success",
        "devices": [class_to_json(device) for device in devices]
    })
