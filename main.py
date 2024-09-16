from threading import Thread
from time import sleep


from utlis.app import app, db
from utlis.data import get_data


def update_data():
    while True:
        with app.app_context():
            data = get_data()
            for device in data:
                db.session.add(device)
            db.session.commit()
        sleep(60)


app.run()
with app.app_context():
    db.create_all()
data_thread = Thread(target=update_data, name="update_data")
data_thread.start()
