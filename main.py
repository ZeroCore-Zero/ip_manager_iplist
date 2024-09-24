from threading import Thread
import asyncio


from utlis.app import app, db
from utlis.data import update_data
from utlis.typical_case import add_typicals
from utlis.websocket import WebSocketServer


async def handle_data():
    websocket = WebSocketServer()
    await websocket.start_server()
    while True:
        new_data = update_data()
        if len(new_data) > 0:
            pass
        websocket.set_message(new_data)
        await asyncio.sleep(60)


def start_handle_data():
    asyncio.run(handle_data())


async def main():
    with app.app_context():
        db.create_all()
        add_typicals(db, ["10.117.251.70", "10.117.251.71"])

    data_thread = Thread(target=start_handle_data, name="handle_data")
    data_thread.start()

    app.run(host="0.0.0.0")


if __name__ == "__main__":
    asyncio.run(main())
