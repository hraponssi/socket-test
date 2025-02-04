import socket
import threading
import time
import struct

data = {"Python": 200, "Scala": 500, "Java": 400, "C++": 300}

def data_as_string():
    build = str(list(data.items())[0])
    for entry in list(data.items())[1:]:
        build += "|" + str(entry)
    return build

def start():
    data_string = data_as_string()
    print(f"Data: {data_string}")
    broadcast_thread = threading.Thread(target=broadcaster, args=())
    broadcast_thread.start()

    server_thread = threading.Thread(target=run_server, args=())
    server_thread.start()

def run_server():
    server_ip = "127.0.0.1"  # server hostname or IP address
    port = 8000  # server port number

    # create a socket object
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to the host and port
        server.bind((server_ip, port))
        # listen for incoming connections
        server.listen()
        print(f"Listening on {server_ip}:{port}")

        while True:
            # accept a client connection
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            # start a new thread to handle the client
            thread = threading.Thread(target=handle_client, args=(client_socket, addr,))
            thread.start()
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.close()

def broadcaster():
    multicast_ip = "224.1.1.1"
    multicast_port = 5004
    try:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ttl = struct.pack('b', 1)
        broadcast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        broadcast_socket.bind((multicast_ip, multicast_port))
        print(f"Bound to broadcast on {multicast_ip}:{multicast_port}")

        while True:
            message = bytes(data_as_string(), "utf-8")
            broadcast_socket.sendto(message, (multicast_ip, multicast_port))
            print(f"Sent multicast broadcast of {message}")
            time.sleep(4)
    except Exception as e:
        print(f"Broadcast error: {e}")
    finally:
        broadcast_socket.close()
        print("Broadcast socket closed")

def handle_client(client_socket, addr):
    try:
        while True:
            # receive and print client messages
            request = client_socket.recv(1024).decode("utf-8")
            if request.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break
            print(f"Received: {request}")
            # Handle query command to get specific data point
            if request.startswith("query "):
                response = "invalid query"
                if request.split(" ")[1] in data:
                    response = str(data[request.split(" ")[1]])
            else:
                # convert and send accept response to the client
                response = "accepted"
            client_socket.send(response.encode("utf-8"))
    except Exception as e:
        print(f"Error when hanlding client: {e}")
    finally:
        client_socket.close()
        print(f"Connection to client ({addr[0]}:{addr[1]}) closed")

start()
