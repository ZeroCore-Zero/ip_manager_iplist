from sqlalchemy import select, update, or_
from threading import Thread
from time import sleep


from utlis.app import app, db
from utlis.data import get_data
from utlis.database import DeviceInfo


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


app.run()
with app.app_context():
    db.create_all()
data_thread = Thread(target=update_data, name="update_data")
data_thread.start()
