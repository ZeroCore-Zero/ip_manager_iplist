import asyncio
import websockets


class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=5678):
        self.host = host
        self.port = port
        self.clients = []
        self.heartbeat_interval = 30

    def __del__(self):
        for client in self.clients:
            client.close()
        self.server.close()

    async def handler(self, websocket):
        print(f"receive connection from {websocket.remote_address}")
        self.clients.append(websocket)
        await websocket.send("heartbeat")

    async def send_heartbeat(self):
        while True:
            for client in list(self.clients):  # 创建客户端列表的副本
                print(f"client {client.remote_address} ", end='')
                if client.open:
                    try:
                        await client.send("heartbeat")
                        print("fine")
                    except websockets.exceptions.ConnectionClosed:
                        self.clients.remove(client)
                        print("closed")
                else:
                    print("closed")
                    self.clients.remove(client)
            await asyncio.sleep(self.heartbeat_interval)

    async def start_server(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f"Websocket Server run on {self.host}:{self.port}")
        asyncio.create_task(self.send_heartbeat())

    def _format_devices_message(self, devices):
        message = f"{len(devices)} New Devices:\n"
        for device in devices:
            message += f"Hostname: {device.HostName}, OnlineTime: {device.OnlineTime}, {'Logged' if device.isLogged else 'Not Logged'}\n"
            message += f"MAC: {device.MAC}, IPv4: {device.IPv4}\n" if device.MAC else ""
            message += f"IAID: {device.IAID}, IPv6: {device.IPv6}\n" if device.IAID else ""
            message += f"DUID: {device.IPv4_DUID}, DHCP_Expiry: {device.IPv4_OutTime}\n"
            message += "\n"
        return message

    async def send_message(self, devices):
        message = self._format_devices_message(devices)
        if self.clients:
            tasks = [client.send(message) for client in self.clients]
            await asyncio.gather(*tasks)
