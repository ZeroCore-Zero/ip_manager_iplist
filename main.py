from utlis.app import app, db


with app.app_context():
    db.create_all()
app.run(host="0.0.0.0")
