from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from concurrent.futures import ThreadPoolExecutor, as_completed


from .config import Config
from .authentication import isLogged


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)


from .database import DeviceInfo


def class_to_json(devices: list[DeviceInfo]):
    executer_pool = ThreadPoolExecutor(max_workers=30)
    ip_list = {}
    executers = {}
    data = []
    for device in devices:
        device_info = {
            "hostname": device.HostName,
            "mac": device.MAC,
            "iaid": device.IAID,
            "duid": device.IPv4_DUID,  # 特例
            "ipv4": device.IPv4,
            "ipv6": device.IPv6,
            "dhcp_expiry": device.IPv4_OutTime,  # 特例
            "onlinesecs": device.OnlineTime.total_seconds()
            # "logged_in": device.isLogged if device.isLogged is not None else isLogged(device.IPv4)
        }
        ip_list[device.IPv4] = device_info
        executers[executer_pool.submit(isLogged, device.IPv4)] = device.IPv4
        data.append(device_info)
    check_list = [
        "duid", "mac", "iaid",
        "ipv4", "ipv6"
    ]
    for item in data:
        for key in check_list:
            if item[key] is None or (isinstance(item[key], str) and len(item[key]) == 0):
                item.pop(key)
    for future in as_completed(executers):
        ip = executers[future]
        result = future.result()
        if result is not None:
            ip_list[ip]["logged_in"] = result
    executer_pool.shutdown()
    print("finish generate")
    return data


@app.route('/all_devices', methods=['GET'])
def get_all_devices():
    devices = DeviceInfo.query.order_by(DeviceInfo.HostName).all()
    return jsonify({
        "status": "success",
        "devices": class_to_json(devices)
    })
