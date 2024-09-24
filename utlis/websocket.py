import asyncio
import websockets


class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=5678, heartbeat_interval=30):
        self.host = host
        self.port = port
        self.heartbeat_interval = heartbeat_interval
        self.message_id = 0

    async def handler(self, websocket):
        print(f"receive connection from {websocket.remote_address}")
        message_id = self.message_id
        while True:
            await asyncio.sleep(self.heartbeat_interval)
            if message_id == self.message_id:
                message = "heartbeat"
            else:
                message_id = self.message_id
                message = self.message
            try:
                await websocket.send(message)
                print(f"send new_data to {websocket.remote_address}")
            except websockets.exceptions.ConnectionClosed:
                print(f"client {websocket.remote_address} closed")
                break

    async def start_server(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Websocket Server run on {self.host}:{self.port}")

    def _format_devices_message(self, devices):
        message = f"{len(devices)} New Devices:\n"
        for device in devices:
            message += f"Hostname: {device.HostName}, OnlineTime: {device.OnlineTime}, {'Logged' if device.isLogged else 'Not Logged'}\n"
            message += f"MAC: {device.MAC}, IPv4: {device.IPv4}\n" if device.MAC else ""
            message += f"IAID: {device.IAID}, IPv6: {device.IPv6}\n" if device.IAID else ""
            message += f"DUID: {device.IPv4_DUID}, DHCP_Expiry: {device.IPv4_OutTime}\n"
            message += "\n"
        return message

    def set_message(self, devices):
        self.message_id += 1
        self.message = self._format_devices_message(devices)
