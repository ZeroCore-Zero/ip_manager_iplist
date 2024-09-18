import requests
from datetime import timedelta
from sqlalchemy import select, update, or_
from threading import Thread
from time import sleep

from .app import db, app
from .database import DeviceInfo


def parse_time(time: str):
    day = int(time.split("/")[0])
    hour, minute, second = list(map(int, time.split("/")[1].split(":")))
    return timedelta(days=day, hours=hour, minutes=minute, seconds=second)


def parse_dhcp(data: str) -> tuple[list[DeviceInfo], list[DeviceInfo]]:
    data = data.splitlines()
    ipv4_devices = []
    ipv6_devices = []
    for lineindex in range(len(data)):
        linedata = data[lineindex].split(" ")
        if linedata[0] == "duid":
            break
        device = DeviceInfo(
            HostName=linedata[3],
            MAC=linedata[1],
            IPv4=linedata[2],
            IPv4_DUID=linedata[4],
            IPv4_OutTime=linedata[0]
        )
        ipv4_devices.append(device)
    for lineindex in range(lineindex + 1, len(data)):
        linedata = data[lineindex].split(" ")
        device = DeviceInfo(
            HostName=linedata[3],
            IAID=linedata[1],
            IPv6=linedata[2],
            IPv6_DUID=linedata[4],
            IPv6_OutTime=linedata[0]
        )
        ipv6_devices.append(device)
    return ipv4_devices, ipv6_devices


def parse_arp(data: str):
    data = data.splitlines()
    devices = []
    for line in data:
        linedata = line.split(" ")
        device = DeviceInfo(
            OnlineTime=parse_time(linedata[1]),
            MAC=linedata[2]
        )
        if "." in linedata[0]:  # ipv4
            device.IPv4 = linedata[0]
        else:  # ipv6
            device.IPv6 = linedata[0]
        devices.append(device)
    return devices


def get_data():
    dhcp_url = "https://yxms.byr.ink/api/dhcp"
    arp_url = "https://yxms.byr.ink/api/arp"

    resp = requests.get(dhcp_url)
    dhcpv4_data, dhcpv6_data = parse_dhcp(resp.text)

    resp = requests.get(arp_url)
    arp_data = parse_arp(resp.text)

    device_data = dhcpv4_data.copy()  # deprecated var dhcpv4_data below
    lookup = {device.HostName: device for device in dhcpv4_data if device.MAC}
    for device in dhcpv6_data:
        if device.HostName in lookup and lookup[device.HostName].IPv6 is None:
            lookup[device.HostName].IAID = device.IAID
            lookup[device.HostName].IPv6 = device.IPv6
            lookup[device.HostName].IPv6_DUID = device.IPv6_DUID
            lookup[device.HostName].IPv6_OutTime = device.IPv6_OutTime
        else:
            device_data.append(device)

    lookup = {
        "ipv4": {device.IPv4: device for device in device_data if device.IPv4 is not None},
        "ipv6": {device.IPv6: device for device in device_data if device.IPv6 is not None}
    }
    for device in arp_data:
        if device.IPv4 in lookup["ipv4"]:
            lookup["ipv4"][device.IPv4].OnlineTime = device.OnlineTime
        else:
            lookup["ipv6"][device.IPv6].OnlineTime = device.OnlineTime

    return device_data


def update_data():
    while True:
        with app.app_context():
            data = get_data()
            for device in data:
                stmt = select(DeviceInfo).where(or_(DeviceInfo.MAC == device.MAC, DeviceInfo.IAID == device.IAID))
                result = db.session.execute(stmt)
                if result.scalar() is not None:
                    # 设备存在，构建更新语句
                    update_stmt = update(DeviceInfo).where(
                        (DeviceInfo.MAC == device.MAC) & (DeviceInfo.IAID == device.IAID)
                    ).values(**{
                        key: getattr(device, key)
                        for key in device.__dict__.keys()
                        if key != "id" and not key.startswith("_")
                    })

                    # 执行更新语句
                    db.session.execute(update_stmt)
                else:
                    # 设备不存在，添加新设备
                    db.session.add(device)
            db.session.commit()
        sleep(60)


data_thread = Thread(target=update_data, name="update_data")
data_thread.start()
