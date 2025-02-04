import socket
import threading
import struct

receiveddata = {}

def data_as_string():
    build = str(list(receiveddata.items())[0])
    for entry in list(receiveddata.items())[1:]:
        build += "|" + str(entry)
    return build

def parseBroadcast(message):
    print("parsing: " + message)
    global receiveddata
    split_message = message.split("|")
    receiveddata = {}
    for entry in split_message:
        entry_split = entry.split(", ")
        receiveddata[entry_split[0][2:-1]] = int(entry_split[1][:-1])
    print("Updated receiveddata to " + data_as_string())

def start():
    b_thread = threading.Thread(target=broadcast_listener, args=())
    c_thread = threading.Thread(target=run_client, args=())
    b_thread.start()
    c_thread.start()

def run_client():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # establish connection with server
    try:
        server_ip = input("Enter server ip: ")
        server_port = int(input("Enter server port: ")) 
        client.connect((server_ip, server_port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        quit()

    try:
        while True:
            # get input message from user and send it to the server
            msg = input("Enter message: ")
            client.send(msg.encode("utf-8")[:1024])

            # receive message from the server
            response = client.recv(1024)
            response = response.decode("utf-8")

            # if server sent us "closed" in the payload, we break out of
            # the loop and close our socket
            if response.lower() == "closed":
                break

            print(f"Received: {response}")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        # close client socket (connection to the server)
        client.close()
        print("Connection to server closed")

def broadcast_listener():
    multicast_ip = "224.1.1.1"
    multicast_port = 5004
    try:
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow multiple sockets to use the same PORT number
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        group = socket.inet_aton(multicast_ip)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        broadcast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        broadcast_socket.bind((multicast_ip, multicast_port))
        print(f"Bound to listen for broadcasts on {multicast_ip}:{multicast_port}")

        while True:
            data, addr = broadcast_socket.recvfrom(1024)
            print(f"Received {data} from {addr}")
            parseBroadcast(str(data)[2:-1])
    except Exception as e:
        print(f"Broadcast receiver error: {e}")
    finally:
        broadcast_socket.close()
        print("Broadcast socket listener closed")


start()