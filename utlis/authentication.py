from bs4 import BeautifulSoup
import socket


def isLogged(ip: str):
    if ip is None:
        return None
    des_ip = "10.3.8.211"
    data = "GET /index HTTP/1.1\r\nHost: 10.3.8.211\r\n\r\n"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_IP, socket.IP_TRANSPARENT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind((ip, 8080))

    sock.settimeout(5)
    try:
        sock.connect((des_ip, 80))
    except TimeoutError:
        return None
    except OSError:
        return None

    sock.sendall(data.encode())
    resp = b''
    try:
        while True:
            resp += sock.recv(4096)
    except TimeoutError:
        sock.settimeout(None)
    resp = resp.decode(errors='ignore')
    sock.close()

    for i in resp.split("\r\n"):
        if i.lower().startswith("<!doctype html>"):
            text = i
            break
    assert 'text' in locals(), resp
    status = BeautifulSoup(text, "lxml").find_all("h3")
    flag = False
    for i in status:
        if "登录成功" in i.text:
            flag = True
    return flag
