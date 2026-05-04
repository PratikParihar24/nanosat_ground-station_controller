import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"LED_ON", ("192.168.137.106", 8888))
print("Fired.")
sock.close()