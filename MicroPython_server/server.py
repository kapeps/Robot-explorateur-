import network

def get_ip():
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    my_ip = "127.0.0.1"

    if not sta_if.active() :
        if ap_if.active() :
            my_ip = ap_if.ifconfig()[0]            

    else :

        my_ip = sta_if.ifconfig()[0]

    return my_ip

print(get_ip())

import socket
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = (get_ip(), 10000)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()

    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            print('received : ' + data.decode("utf-8"))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no more data from', client_address)
                break
            
    finally:
        # Clean up the connection
        connection.close()

    