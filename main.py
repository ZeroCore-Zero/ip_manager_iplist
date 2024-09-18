from threading import Thread


from utlis.app import app, db
from utlis.data import update_data


with app.app_context():
    db.create_all()

data_thread = Thread(target=update_data, name="update_data")
data_thread.start()

app.run(host="0.0.0.0")
