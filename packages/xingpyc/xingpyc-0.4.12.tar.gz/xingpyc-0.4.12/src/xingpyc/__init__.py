from multiprocessing import Process
import asyncio
import os
from websockets.sync.client import connect
from websockets.server import serve
from websocket import WebSocket

import time
import numpy as np
from threading import Thread
from io import BytesIO
import PIL.Image as Image
import uuid
import socket
os.environ["CRYPTOGRAPHY_OPENSSL_NO_LEGACY"] = "1"
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

BLOCK_SIZE=500000

def image_to_png_bytestring(image):
    png_bytestring = BytesIO()
    image.save(png_bytestring, format="PNG")
    png_bytestring.seek(0)
    return png_bytestring.getvalue()

def image_to_webp_bytestring(image,quality=80):
    webp_bytestring = BytesIO()
    image.save(webp_bytestring, format="WEBP", quality=quality)
    webp_bytestring.seek(0)
    return webp_bytestring.getvalue()

def write_progress(task_name, progress):
    with open(f"progress/{task_name}", "w") as f:
        f.write(progress)

def decode_concat_block(buffer):
    # Read the first 10 bytes to get the header size
    header = buffer[0:10]
    header_size = int(header.decode('utf-8'))

    # Extract the header JSON string
    header_json = buffer[10:10 + header_size].decode('utf-8')
    header = json.loads(header_json)

    # Extract the data blocks
    data_blocks = {}
    for key,value in header.items():
        pointer = value['pointer']
        size = value['size']
        data_block = buffer[10 + header_size + pointer : 10 + header_size + pointer + size]
        data_blocks[key] = data_block

    return data_blocks

def open_image_from_bytes(image_bytes):
    # Convert byte string to a file-like object
    image_stream = BytesIO(image_bytes)
    # Open the image using PIL
    image = Image.open(image_stream)
    return image

def get_device_id_env():
    if os.path.exists(".device_id"):
        device_id = open(".device_id", "r").read()
    else:
        print("Device ID not found, generating new one")
        device_id = str(uuid.uuid4())
        open(".device_id", "w").write(device_id)
    return device_id[0:10]

print_time= {}
def print_interval(key,message,interval):
    if key not in print_time or time.time() - print_time[key] > interval:
        print(message)
        print_time[key] = time.time()

def error_log(*message):
    #print in red
    print("\033[91m", *message, "\033[0m")

def warning_log(*message):
    #print in yellow
    print("\033[93m", *message, "\033[0m")

def success_log(*message):
    #print in green
    print("\033[92m", *message, "\033[0m")
    
def get_local_ip():
    try:
        # Create a dummy socket and connect to a remote server to determine the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Use a common public server (like Google DNS) to establish a connection
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return f"Unable to get local IP: {e}"

# Redirect sys.stdout to the custom stream
class XClient:
    XClients = []
    def __init__(self, async_funcs,sync_funcs, mode: str, ip=None, portOrInfo=None):
        """
        init a ComClient with AI functions
        funcs: a list of AI functions
        """
        self.cloudClient = None
        self.incomingMsg = []
        self.clients = {}
        self.blockbuffers = {}
        self.processor_status = set()
        # Initialize device ID from environment variable
        self.device_id = get_device_id_env()
        self.ip = ip
        self.portOrInfo = portOrInfo
        self.need_reconnect_cloud = False
        self.lastRTCCheckTime = time.time()
        XClient.XClients.append(self)
        self.setup_peer_connection()
        # tasks folder is for placing incoming commands
        if not os.path.exists("tasks"):
            os.mkdir("tasks")
        tasks = os.listdir("tasks")
        for task in tasks:
            os.remove(f"tasks/{task}")
        # results folder is for placing results from various AI functions, no matter binded to XClient or not
        if not os.path.exists("results"):
            os.mkdir("results")
        results = os.listdir("results")
        for result in results:
            os.remove(f"results/{result}")
        if not os.path.exists("progress"):
            os.mkdir("progress")
        progresses = os.listdir("progress")
        for p in progresses:
            os.remove(f"progress/{p}")
        # message loop
        asyncio.get_event_loop().create_task(self.message_loop())

        # listening
        if mode == "server":
            print(
                "\033[93m Server started on " + ip + ":" + str(portOrInfo) + " \033[0m"
            )
            asyncio.get_event_loop().run_until_complete(
                serve(self.asServer_listening, ip, portOrInfo)
            )
        elif mode == "client":
            # for client mode, connect to the cloud server, use sync websocket, async one is not working well for now
            self.need_reconnect_cloud = True

        # for functions registered with XClient, create a process for each processor that will automatically listen according to there function name
        # e.g. if there is a function named "i2i" in the list, a process will be created to listen for "i2i" header tasks in the tasks folder
        for func in async_funcs:
            Process(target=add_listener, args=(func,)).start()

        self.sync_funcs = {func.__name__: func for func in sync_funcs}
            
        asyncio.get_event_loop().run_forever()

    def setup_peer_connection(self):
        warning_log("Setting up peer connection")
        self.data_channel_opened = False
        self.pc = RTCPeerConnection()
        self.rtcChannel = None
        self.lastRTCCheckTime = time.time()

        @self.pc.on('datachannel')
        def on_datachannel(channel):
            self.rtcChannel = channel
            success_log("Data channel created:", channel)
            self.data_channel_opened = True
            self.lastRTCCheckTime = time.time()

            @channel.on("message")
            def on_message(message):
                # Handle received message
                # Send a response
                if message == "check":
                    channel.send("check back")
                    self.lastRTCCheckTime = time.time()
                    print_interval("a","\033[93m data channel is alive \033[0m",3)
                    return
                print("Received message:", message)
                # an example i2i for testing
                _time = time.time()
                screenshot = sct.grab({"top": 60, "left": 0, "width": 1920, "height": 1080})

                # Convert the raw screenshot data to a NumPy array
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
                print("capture time:", time.time()-_time)
                
                bytesio = BytesIO()
                img.save(bytesio, format='JPEG', quality=90)
                # webp_buffer = image_to_png_bytestring(img)
                print("streaming time:", time.time()-_time)
                channel.send(bytesio.getvalue())
            
            @channel.on("close")
            def on_close():
                print("\033[93m","Data channel closed","\033[0m")
                self.setup_peer_connection()
                print("\033[93m","reset peer connection","\033[0m")
                #XClient.pc = RTCPeerConnection()#reset the peer connection

    def cloud_connect(self): 
        try:
            print("\033[93m connecting to server \033[0m")
            self.cloudClient = WebSocket()
            self.cloudClient.connect(self.ip)
            self.cloudClient.send_bytes(
                ("login     " + self.device_id + self.portOrInfo).encode("utf-8")
            )
            account_name = self.portOrInfo.split(".")[0]
            login_res = self.cloudClient.recv()
            if login_res == b"login success":
                print("\033[95m===========  Login Success!\033[0m")
                print("\033[95m===========  Welcome:",account_name,"\033[0m")
                print("\033[95m===========  Device:",self.device_id,"\033[0m")
            else:
                error_log("Login failed")
                error_log(str(login_res))
                return False
            Thread(target=self.asClient_listening, args=()).start()
            return True
        except Exception as e:
            print(f"Error in connecting to cloud: {e}")
            return False

    async def message_loop(self):
        """
        the looping function for sending and receiving messages
        """
        warning_log("=== message loop started ===")
        loopCount = 0
        while True:
            loopCount += 1
            if self.need_reconnect_cloud:
                if self.cloud_connect():
                    self.need_reconnect_cloud = False
                time.sleep(1)
                continue

            if time.time() - self.lastRTCCheckTime > 3 and self.data_channel_opened or self.pc.signalingState == "closed":
                error_log("No check received for 3 seconds, reset peer connection")
                self.setup_peer_connection()
            
            check_interval = 300
            if len(self.processor_status)==0:
                check_interval = 30#check more frequently if no processor is running, asking server for new tasks

            if loopCount % check_interval == 0 and self.cloudClient is not None:
                running_processors = [h for h in self.processor_status]
                running_processors_str = " ".join(running_processors)
                self.cloudClient.send_bytes("check     0000000000"+running_processors_str)
                print_interval("c","check to cloud",10)

            ### here starts the incoming message processing
            ### here starts the incoming message processing
            ### here starts the incoming message processing
            inputMsg = []
            outputs=[]
            while len(self.incomingMsg) != 0:
                inputMsg.append(self.incomingMsg.pop())
            for client_id, message in inputMsg:

                if type(message) == str:
                    message = message.encode("utf-8")#just in case, happens sometimes

                print(
                    "\033[93mheader:"
                    + message[:10].replace(b" ", b"").decode()
                    + "   id:"
                    + message[10:20].decode()
                    + "   length:"
                    + str(len(message[20:]))
                    + "\033[0m"
                )
                # connect client and save client id
                header = message[:10].replace(b" ", b"").decode()
                task_id = message[10:20]
                task_id_str = task_id.decode()
                content = message[20:]

                try:
                    if self.rtcChannel is not None:
                        self.rtcChannel.send("check")
                except Exception as e:
                    print("\033[91m", "Error sending message to data channel:", str(e), "\033[0m")
                    self.data_channel_opened = False
                try:
                    if header == "check":
                        print("connect check received")
                    elif header[0:5] == "block":
                        # if block, save it to buffer
                        if task_id_str not in self.blockbuffers:
                            self.blockbuffers[task_id_str] = []
                        block_idx = int(header[5:10])
                        self.blockbuffers[task_id_str].append({"idx":block_idx,"data":content})
                        print(len(self.blockbuffers[task_id_str]), "blocks received")
                    else:
                        # if sending is complete, proceed to process the file
                        if task_id_str in self.blockbuffers:
                            # if there is a block buffer, concat it
                            self.blockbuffers[task_id_str].append({"idx":99999,"data":content})
                            sorted_blocks = sorted(self.blockbuffers[task_id_str], key=lambda x: x["idx"])
                            content = b"".join([block["data"] for block in sorted_blocks])
                            del self.blockbuffers[task_id_str]  # clean buffer
                        # finally write the file to tasks folder for processing from other processes
                        if header in self.sync_funcs:#if it is a sync function
                            func = self.sync_funcs[header]
                            #if async, use await
                            if asyncio.iscoroutinefunction(func):
                                res = await func(content)
                            else:
                                res = func(content)
                            assert type(res) == bytes, "Return type must be bytes"
                            file_str = f"{client_id}.{task_id.decode()}.{header}"
                            outputs.append([file_str, res])
                        else:#if it is not a sync function
                            self.processor_status.add(header)#only add async functions to processor status
                            with open(
                                f"tasks/{client_id}.{task_id.decode()}.{header}", "wb"
                            ) as f:
                                print(
                                    "place task: "
                                    + f"{client_id}.{task_id.decode()}.{header}"
                                )
                                f.write(content)
                except Exception as e:
                    print(f"Error in websocket communication: {e}")
                    continue
            
            ### here starts the progress reporting
            ### here starts the progress reporting
            ### here starts the progress reporting
            if len(os.listdir("progress")) > 0:
                for task_id in os.listdir("progress"):
                    try:
                        progress_content = open(f"progress/{task_id}", "r").read()
                        if len(task_id) != 10:
                            raise "invalid task id length!!"
                        task_id_byte = task_id.encode("utf-8")
                        progress_content = progress_content.encode("utf-8")

                        if client_id == -1:#cloud
                            print("start sending progress to cloud")
                            self.cloudClient.send_bytes(b"progress  " + task_id_byte + progress_content)
                            print("sent progress to cloud")
                        else:#client
                            await websocket.send(b"progress  " + task_id_byte + progress_content)
                        os.remove(f"progress/{task_id}")
                    except Exception as e:
                        print(f"Error in sending progress to websocket: {e}")

            ### here starts the result sending
            ### here starts the result sending
            ### here starts the result sending
            if len(os.listdir("results")) > 0:
                for file in os.listdir("results"):
                    try:
                        with open(f"results/{file}", "rb") as f:
                            result_data = f.read()
                            outputs.append([file,result_data])
                        os.remove(f"results/{file}")
                    except Exception as e:
                        print(f"Error in reading result file: {e}")
            
            for file, result_data in outputs:
                try:
                    content = result_data
                    client_id, task_id, header = file.split(".")
                    client_id = int(client_id)
                    if header in self.processor_status:#sync functions are not in processor status
                        self.processor_status.remove(header)
                    header = (header + " " * (10 - len(header))).encode("utf-8")
                    if isinstance(task_id, str):
                        task_id = task_id.encode("utf-8")
                    if isinstance(header, str):
                        header = header.encode("utf-8")
                    if isinstance(content, str):
                        content = content.encode("utf-8")
                    if client_id == -1:
                        print("start sending to cloud")
                        count = 0
                        totalblocks = len(content) // BLOCK_SIZE
                        while len(content) > BLOCK_SIZE*2:
                            block_header="block00000"
                            block_header = block_header[:10-len(str(count))]+str(count)
                            block_header = block_header.encode("utf-8")
                            Thread(
                                target=self.cloudClient.send_bytes,
                                args=(
                                    block_header + task_id + content[0:BLOCK_SIZE],
                                ),
                            ).start()
                            time.sleep(0.1)# in case server cannot receive in the right order
                            content = content[BLOCK_SIZE:]
                            print(f"sent block {count}/{totalblocks}")
                            count += 1
                        self.cloudClient.send_bytes(header + task_id + content)
                        print("sent to cloud")
                except Exception as e:
                    print(f"Error in sending message to websocket: {e}")
            else:
                await asyncio.sleep(0.01)


    def asClient_listening(self):
        try:
            while True:
                message = self.cloudClient.recv()
                ###### -1 should be client id, change it later
                self.incomingMsg.append((-1, message))
        except Exception as e:
            self.need_reconnect_cloud = True
            print("Connection closed by the server")

    async def asServer_listening(self, websocket):
        client_id = id(websocket)
        print(f"Client {client_id} connected")
        try:
            async for message in websocket:
                self.clients[client_id] = websocket
                self.incomingMsg.append((client_id, message))
        except Exception as e:
            print(f"Error in websocket communication: {e}")


def add_listener(callback, interval=0.1):
    while True:
        taskfiles = os.listdir("tasks")
        time.sleep(interval)
        if len(taskfiles) == 0:
            continue
        try:
            for file in taskfiles:
                client_id, task_id, header = file.split(".")
                if header == callback.__name__:
                    res = callback("tasks/" + file)
                    assert type(res) == bytes, "Return type must be bytes"
        except Exception as e:
            print(f"Error in interpreting task of {callback.__name__}: {e}")
            res = b"failed"
        
        try:
            if file is not None:
                with open("results/" + file, "wb") as f:
                    f.write(res)
            os.remove("tasks/" + file)
        except Exception as e:
            print(f"Error in writing result of {callback.__name__}: {e}")


def i2i(data):
    # an example i2i for testing
    print("i2i task received, doing image flipping")
    data = open(data, "rb").read()
    data = decode_concat_block(data)
    config = data["config"].decode("utf-8")
    config = json.loads(config)
    img = open_image_from_bytes(data["image"])
    #img = Image.open(BytesIO(imgFile))
    nparray = np.array(img)
    # do something that fake the AI function
    nparray = np.flip(nparray, axis=1)
    img = Image.fromarray(nparray)

    webp_buffer = image_to_webp_bytestring(img)

    return webp_buffer


def stream(_):
    import mss
    sct = mss.mss()
    # an example i2i for testing
    _time = time.time()
    screenshot = sct.grab({"top": 60, "left": 0, "width": 1920//1.3, "height": 1080//1.3})

    # Convert the raw screenshot data to a NumPy array
    img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
    print("capture time:", time.time()-_time)
    bytes = BytesIO()
    img.save(bytes, format='JPEG', quality=90)
    # webp_buffer = image_to_png_bytestring(img)
    print("streaming time:", time.time()-_time)
    return bytes.getvalue()


import json
try:
    import mss
    sct = mss.mss()
except:
    print("mss not supported")

async def rtc(jsonByte):
    xclient:XClient = XClient.XClients[0]
    xclient.lastRTCCheckTime = time.time()
    sdpstr = jsonByte.decode("utf-8")
    offer_sdp = RTCSessionDescription(sdp=sdpstr, type="offer")
    await xclient.pc.setRemoteDescription(offer_sdp)
    answer = await xclient.pc.createAnswer()
    await xclient.pc.setLocalDescription(answer)
    res = xclient.pc.localDescription
    resJson = json.dumps({"sdp":res.sdp,"type":res.type})
    return resJson.encode("utf-8")

async def ice(data):
    try:
        # Decode the incoming data
        jsonStr = data.decode("utf-8")
        dict = json.loads(jsonStr)
        ip = dict["ip"]
        protocol = dict["protocol"]
        component = dict["component"]
        foundation = dict["foundation"]
        port = dict["port"]
        priority = dict["priority"]
        candidate_type = dict["type"]
        sdp_mid = dict["sdpMid"]
        sdp_mline_index = dict["sdpMLineIndex"]

        # if len(ip) >20 or protocol!="udp":#ipv6
        #     print("\033[92m", "=========skip ipv6===========", ip, "\033[0m")
        #     return b"skip ipv6"
        

        # Create an ICE candidate object
        ice_candidate = RTCIceCandidate(
            component=component,
            foundation=foundation,
            ip=ip,
            port=port,
            priority=priority,
            protocol=protocol,
            type=candidate_type,
            sdpMid=sdp_mid,
            sdpMLineIndex=sdp_mline_index
        )
        
        # Add the ICE candidate to the peer connection
        xclient = XClient.XClients[0]
        await xclient.pc.addIceCandidate(ice_candidate)
        print("\033[92m", "Added ICE candidate:", ice_candidate, "\033[0m")
        return b"done"

    except Exception as e:
        print("\033[91m", "Error adding ICE candidate:", str(e), "\033[0m")
        return b"error"

if __name__ == "__main__":
    TESTING_CLOUD = True
    if TESTING_CLOUD:
        XClient([i2i],[rtc,ice], "client", "wss://www.xing.art/com/", "alpha.alpha")
    else:
        XClient([i2i],[stream], "server", get_local_ip(), "8088") #for local
