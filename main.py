from threading import Thread


from utlis.app import app, db
from utlis.data import update_data
from utlis.typical_case import add_typicals


with app.app_context():
    db.create_all()
    add_typicals(db, ["10.117.251.70", "10.117.251.71"])

data_thread = Thread(target=update_data, name="update_data")
data_thread.start()

app.run(host="0.0.0.0")
