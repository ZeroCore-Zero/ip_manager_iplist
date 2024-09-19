from sqlalchemy import select


from .database import DeviceInfo


def get_typicals(ip_list: list[str]):
    result = []
    for ip in ip_list:
        result.append(DeviceInfo(
            HostName="*",
            MAC="MAC to live",
            IAID="IAID to live",
            IPv4=ip
        ))
    return result


def add_typicals(db, ip_list):
    typicals = get_typicals(ip_list)
    for device in typicals:
        stmt = select(DeviceInfo).where(DeviceInfo.IPv4 == device.IPv4)
        if db.session.execute(stmt).first() is None:
            db.session.add(device)
    db.session.commit()
