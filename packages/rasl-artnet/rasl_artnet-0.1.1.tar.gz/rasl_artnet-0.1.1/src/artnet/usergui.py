import tkinter as tk
from tkinter import messagebox, filedialog
import zmq
from zmq.devices import ProcessProxySteerable
import pyaudio
from multiprocessing import freeze_support, Event, Process, Manager
from concurrent.futures import Future, ProcessPoolExecutor, wait
from . import dataFrame
import time
from datetime import datetime
import socket
from timeit import default_timer as timer
import random
import sys
import csv
import traceback
from pathlib import Path
import os


streamerFrontPort = 5559
streamerBackPort = 5556
voiceFrontPort = 5561
voiceBackPort = 5562

tcpDataPubPort = 5600
tcpDataPubMonPort = 5601
tcpDataPubCtrlPort = 5602
tcpDataSubPort = 5603
tcpDataSubMonPort = 5604
tcpDataSubCtrlPort = 5605
tcpVoicePubPort = 5606
tcpVoicePubMonPort = 5607
tcpVoicePubCtrlPort = 5608
tcpVoiceSubPort = 5609
tcpVoiceSubMonPort = 5610
tcpVoiceSubCtrlPort = 5611



chunkProportion = 50


def createPublisherStream(name:str, p, inputDeviceIndex,audioRate, tcpVoicePub):
    RATE = audioRate
    CHUNK = int(RATE / chunkProportion)

    context = zmq.Context.instance()
    publisher = context.socket(zmq.PUB)
    publisher.connect(tcpVoicePub)
    count = 0
    encName = name.encode()

    def callback(in_data, frame_count, time_info, status):
        # print(f'Sending voice as {encName}')
        nonlocal count
        if count == 0:
            publisher.send_multipart([b'Connection',encName,datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').encode()])
        publisher.send_multipart([encName, in_data, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').encode()])
        count = (count + 1)%(2*chunkProportion)
        return (in_data, pyaudio.paContinue)

    stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=RATE,
                input=True,
                input_device_index = inputDeviceIndex,
                output=False,
                frames_per_buffer=CHUNK,
                stream_callback=callback)
    # stream.start_stream()
    return stream
    

def createSubscriberStream(connName:bytes, connections, outputDeviceIndex,audioRate,tcpVoiceSub):
    p = pyaudio.PyAudio()
    RATE = audioRate
    CHUNK = int(RATE / chunkProportion)
    # CHUNK = 512
    context = zmq.Context.instance()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(tcpVoiceSub)
    subscriber.subscribe(connName)
    # subscriber.subscribe("")
    dataLength = CHUNK * 4
    
    def callback(in_data, frame_count, time_info, status):
        data = bytes(dataLength)
        while True:
            try:
                msg = subscriber.recv_multipart(flags=zmq.NOBLOCK)
                id = msg[0].decode()
                data = msg[1]
                # print(f'Received voice from {connName}')
                print(f'recvd voice from {id}')
            except Exception:
                break
                
        # event = subscriber.poll(timeout=250)
        # if event == 0:
        #     # connections.remove(connName)
        #     print(f'no voice data for {connName.decode()}')
        #     data = bytes(dataLength)
        # else:
        #     data = subscriber.recv_multipart()
        #     id = data[0].decode()
        #     data = data[1]
        #     # print(f'Received voice from {connName}')
        #     print(f'recvd voice from {id}')
        return (data, pyaudio.paContinue)
    stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=RATE,
                input=False,
                output=True,
                output_device_index = outputDeviceIndex,
                frames_per_buffer=CHUNK,
                stream_callback=callback)
    # stream.start_stream()
    return stream

def parsetodict(message):
    mydict= {}
    for i in range(len(message)):
        jointarr = message[i].split(" ")
        if(len(jointarr)==8):
            mydict[int(jointarr[1])] = [float(jointarr[2][2:]), float(jointarr[3][2:]), float(jointarr[4][2:]), float(jointarr[5][2:]), float(jointarr[6][2:]), float(jointarr[7][2:])]
        else:
            mydict[int(jointarr[0])] = [float(jointarr[1][2:]), float(jointarr[2][2:]), float(jointarr[3][2:]),float(jointarr[4][2:]), float(jointarr[5][2:]), float(jointarr[6][2:])]
    return mydict

def parsetodictbl(message):
    mydict= {}
    for val in message:
        dictentry = val.split(":")
        mydict[int(dictentry[0])] = float(dictentry[1])
    return mydict

def TestDataStreamFun(numMuscles, numBlendshapes, numPriorities, hz, id, debug, stopEvent, tcpDataPub):
    def log(msg):
        if debug:
            print(msg)

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.connect(tcpDataPub)

    duration = 1
    frame = dataFrame.DataFrame()
    while not stopEvent.is_set():
        
        frame.id = id
        start = timer()
        end = timer()
        while(end - start < (1.0 / hz)):
            end = timer()
        for i in range(numMuscles):
            for j in range(1,numPriorities+1):
                for k in range(6):
                    frame.muscles[i].entries[j].values.append(random.random())
                frame.muscles[i].entries[j].priority = j
                frame.muscles[i].entries[j].timestamp.GetCurrentTime()
                frame.muscles[i].entries[j].duration.FromSeconds(duration)
        msg = [id.encode(),frame.SerializeToString(),datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').encode()]
        zmq_socket.send_multipart(msg)
        end = timer()
        frame.Clear()

def DataStreamFun(debug, udp_ip, udp_port,id, stopEvent,tcpDataPub):
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.connect(tcpDataPub)
    sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
    sock.bind((udp_ip, udp_port))
    duration = 1
    frame = dataFrame.DataFrame()
    frame2 = dataFrame.DataFrame()
    while not stopEvent.is_set():
        start= timer()
        end = timer()
        data, addr = sock.recvfrom(15000) #anything else was too small 
       
        secondSplit = []
        firstSplit = str(data).split(',')
        for i in range(len(firstSplit)-1):
            secondSplit.append(firstSplit[i].split(':')[1])
        if(secondSplit[0]=='true'):
            frame.muscles[0].entries[1].values.append(float(1))
        elif(secondSplit[1] == 'false'):
            frame.muscles[0].entries[1].values.append(0.0)

        frame.muscles[0].entries[1].priority = 1
        frame.muscles[0].entries[1].timestamp.GetCurrentTime()
        frame.muscles[0].entries[1].duration.FromSeconds(duration)

        for i in range(1,73):
            thirdsplit = secondSplit[i].split(' ')
            for j in range(len(thirdsplit)):
                frame.muscles[i].entries[1].values.append(float(thirdsplit[j][2:]))

                frame.muscles[i].entries[1].priority = 1
                frame.muscles[i].entries[1].timestamp.GetCurrentTime()
                frame.muscles[i].entries[1].duration.FromSeconds(duration)
        
        for i in range(73,131):
            frame.muscles[i].entries[1].values.append(float(secondSplit[i]))
            frame.muscles[i].entries[1].priority = 1
            frame.muscles[i].entries[1].timestamp.GetCurrentTime()
            frame.muscles[i].entries[1].duration.FromSeconds(duration)

            # frame.blendshapes[1].entries[1].values.append(0)
            # frame.blendshapes[1].entries[1].priority = 1
            # frame.blendshapes[1].entries[1].timestamp.GetCurrentTime()
            # frame.blendshapes[1].entries[1].duration.FromSeconds(duration)

        zmq_socket.send_multipart([id.encode(),frame.SerializeToString(),datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').encode()])
        frame.Clear()

def TestSubscriberFun(debug, stopEvent, tcpDataSub):

    context = zmq.Context()

    subscriber = context.socket(zmq.SUB)
    subscriber.connect(tcpDataSub)
    subscriber.subscribe("")

    print(f'Subscriber started. Connected to {tcpDataSub}')
    while not stopEvent.is_set():
        event = subscriber.poll(timeout=250)
        if event == 0:
            # connections.remove(connName)
            pass
        else:
            message = subscriber.recv_multipart()
            id = message[0].decode()
            print(f'Receive data from User {id}')
    

def SubscriberFun(debug, localHostUDP_IP, subscriberUDP_PORT, numMuscles, ids_dict, stopEvent, tcpDataSub):
    def log(msg):
        if debug:
            print(msg)

    IP_Port = (localHostUDP_IP, subscriberUDP_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(tcpDataSub)
    # subscriber.subscribe("")
    print(ids_dict)
    for i in range(5):
        if(ids_dict[i+1]==True):
            subscriber.subscribe("User " + str(i+1))
    state = dataFrame.AvatarState()
    #id = "User " + i
    avgLag = 0
    n = 1
    start = timer()
    
    while not stopEvent.is_set():
    #print("Waiting to receive!")
        send_dict = {}
        for i in range(numMuscles): #change to variableplease
            send_dict[i] = []

        message = subscriber.recv_multipart()
        id = message[0]
        data = message[1]
        # msg = subscriber.recv_multipart()
        # message = msg[1]
        end = timer()
        log(f'Received Hz: {1.0/(end - start)}')
        start = timer() 
        state.ParseFromString(data)

        for key, muscle in state.muscles.items():
            for i in muscle.values:
                send_dict[int(key)].append(i)
        sendString = ''
        for i in range(numMuscles):
            temp = "".join(str(x) + " " for x in send_dict[i])
            sendString= sendString + temp + ','
        sendString = sendString + str(id)
        sock.sendto(sendString.encode('utf-8'),IP_Port)

def CreateSendProxy(socketTypes:tuple, endpoints:tuple):
    proxy = ProcessProxySteerable(*socketTypes)
    proxy.bind_in(endpoints[0])
    if socketTypes[0] == zmq.SUB:
        proxy.setsockopt_in(zmq.SUBSCRIBE,b'')
    proxy.connect_out(endpoints[1])
    proxy.bind_mon(endpoints[2])
    proxy.bind_ctrl(endpoints[3])
    proxy.start()
    ctx = zmq.Context.instance()
    ctrl = ctx.socket(zmq.REQ)
    ctrl.connect(endpoints[3])
    return (ctrl,proxy.context_factory())

def CreateReceiveProxy(socketTypes:tuple, endpoints:tuple):

    proxy = ProcessProxySteerable(*socketTypes)
    proxy.connect_in(endpoints[0])
    if socketTypes[0] == zmq.SUB:
        proxy.setsockopt_in(zmq.SUBSCRIBE,b'')
    proxy.bind_out(endpoints[1])
    proxy.bind_mon(endpoints[2])
    proxy.bind_ctrl(endpoints[3])
    proxy.start()
    ctx = zmq.Context.instance()
    ctrl = ctx.socket(zmq.REQ)
    ctrl.connect(endpoints[3])
    return (ctrl,proxy.context_factory())

def Monitor(rootDir: Path, pair:str, session:str, userId:str, connectionName:str, socket:str, endpoint:str, dtime:str,  stopEvent):

    userId = userId.replace(' ','')
    
    folder = rootDir.joinpath(rootDir,'data','NetworkLogs',pair,session, userId)

    folder.mkdir(parents=True,exist_ok=True)

    filename = os.path.join(folder,f'Log_{userId}_{connectionName}_{socket}_{dtime}')

    fields = ['Datetime','Pair','Session','User','ConnectionType', 'SocketType','Topic','Size','SendDateTime']
    activityLog = []

    try:
        context = zmq.Context()
        monitor = context.socket(zmq.SUB)
        monitor.connect(endpoint)
        monitor.subscribe('')
        
        while not stopEvent.is_set():
            event = monitor.poll(timeout=250)
            if event == 0:
                pass
            else:
                msg = monitor.recv_multipart()
                curSize = sum([sys.getsizeof(entry)/ 1000.0 for entry in msg])
                sendDateTime = None
                if len(msg) < 3:
                    sendDateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                else:
                    sendDateTime = msg[2].decode()
                activityLog.append([datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), pair, session, userId, connectionName, socket, msg[0].decode().replace(' ',''), curSize, sendDateTime])
        
        with open(f'{filename}.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(activityLog)
            return [f'Wrote log for {userId}:{connectionName}:{socket} to {filename}.csv']
    except Exception:
        errmsg = traceback.format_exc()
        with open(f'{filename}_error.txt', 'w') as errlog, open(f'{filename}.csv', 'w', newline='') as csvfile:
            errlog.write(errmsg)
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvwriter.writerows(activityLog)
        return [errmsg, f'Wrote log for {userId}:{connectionName}:{socket} to {filename}.csv']

def createPromptGUI():
    proxyCtrls = []
    multiManager = Manager()
    stopEvent = multiManager.Event()
    initEvent = multiManager.Event()
    stopEvent.set()
    initEvent.clear()
    monitorExecutor = ProcessPoolExecutor(max_workers = 8)
    monitorFutures = []
    streams = []
    connections = []
    processes = []
    context = []
    p = pyaudio.PyAudio()
    dtime = None
    rootDir = Path.cwd().parent
    inputDeviceIndex = None
    outputDeviceIndex = None
    audioRate = None
    name = None
    debug = None
    localTesting = None
    voiceLoopback = None
    pair = None
    session = None
    streamerUDP_IP = None
    streamerUDP_PORT = None
    localHostUDP_IP = None
    subscriberUDP_PORT = None
    numMuscles = None
    numBlendshapes = None
    numPriorities = None
    datastreamHz = None
    address = None
    portMultiple = None


    def connect():
        #check if already running
        if not stopEvent.is_set():
            return
        # start running
        stopEvent.clear()

        if not processGuiInput():
            return
        
        nonlocal context
        context = zmq.Context()

        tcpDataPub = f'tcp://127.0.0.1:{tcpDataPubPort+12*portMultiple}'
        tcpDataPubMon = f'tcp://127.0.0.1:{tcpDataPubMonPort+12*portMultiple}'
        tcpDataPubCtrl = f'tcp://127.0.0.1:{tcpDataPubCtrlPort+12*portMultiple}'
        tcpDataSub = f'tcp://127.0.0.1:{tcpDataSubPort+12*portMultiple}'
        tcpDataSubMon = f'tcp://127.0.0.1:{tcpDataSubMonPort+12*portMultiple}'
        tcpDataSubCtrl = f'tcp://127.0.0.1:{tcpDataSubCtrlPort+12*portMultiple}'
        tcpVoicePub = f'tcp://127.0.0.1:{tcpVoicePubPort+12*portMultiple}'
        tcpVoicePubMon = f'tcp://127.0.0.1:{tcpVoicePubMonPort+12*portMultiple}'
        tcpVoicePubCtrl = f'tcp://127.0.0.1:{tcpVoicePubCtrlPort+12*portMultiple}'
        tcpVoiceSub = f'tcp://127.0.0.1:{tcpVoiceSubPort+12*portMultiple}'
        tcpVoiceSubMon = f'tcp://127.0.0.1:{tcpVoiceSubMonPort+12*portMultiple}'
        tcpVoiceSubCtrl = f'tcp://127.0.0.1:{tcpVoiceSubCtrlPort+12*portMultiple}'

        # proxy config variables
        dataPubSockets = (zmq.PULL, zmq.PUSH, zmq.PUB, zmq.REP)
        dataPubEndpoints = (tcpDataPub,f'tcp://{address}:{streamerFrontPort}',tcpDataPubMon,tcpDataPubCtrl)
        dataSubSockets = (zmq.SUB, zmq.PUB, zmq.PUB, zmq.REP)
        dataSubEndpoints = (f'tcp://{address}:{streamerBackPort}', tcpDataSub, tcpDataSubMon, tcpDataSubCtrl)
        voicePubSockets = (zmq.SUB, zmq.PUB, zmq.PUB, zmq.REP)
        voicePubEndpoints = (tcpVoicePub,f'tcp://{address}:{voiceFrontPort}', tcpVoicePubMon, tcpVoicePubCtrl)
        voiceSubSockets = (zmq.SUB, zmq.PUB, zmq.PUB, zmq.REP)
        voiceSubEndpoints = (f'tcp://{address}:{voiceBackPort}', tcpVoiceSub, tcpVoiceSubMon, tcpVoiceSubCtrl)
                
        # start voice chat
        connections.append(name.encode())
        streams.append(createPublisherStream(name, p, inputDeviceIndex,audioRate, tcpVoicePub))
        if voiceLoopback:
            print('Voice Loopback Enabled')
            streams.append(createSubscriberStream(name.encode(),connections,outputDeviceIndex,audioRate,tcpVoiceSub))
        # connThread = Thread(target=updateConnections, args=(voiceBackendIP,outputDeviceIndex,audioRate))
        # connThread.start()
        
        subscriber = context.socket(zmq.SUB)        
        subscriber.connect(tcpVoiceSub)
        subscriber.subscribe(b'Connection')
        root.after(25,updateConnections,subscriber,outputDeviceIndex,audioRate, tcpVoiceSub)

        # start proxies and monitors
        proxyCtrls.append(CreateSendProxy(dataPubSockets,dataPubEndpoints))
        proxyCtrls.append(CreateReceiveProxy(dataSubSockets,dataSubEndpoints))
        proxyCtrls.append(CreateSendProxy(voicePubSockets,voicePubEndpoints))
        proxyCtrls.append(CreateReceiveProxy(voiceSubSockets,voiceSubEndpoints))

        monitorFutures.append(monitorExecutor.submit(Monitor,rootDir,pair,session, name,"data","Pub", tcpDataPubMon,dtime,stopEvent))
        monitorFutures.append(monitorExecutor.submit(Monitor,rootDir,pair,session, name,"data","Sub", tcpDataSubMon,dtime,stopEvent))
        monitorFutures.append(monitorExecutor.submit(Monitor,rootDir,pair,session, name,"voice","Pub", tcpVoicePubMon,dtime,stopEvent))
        monitorFutures.append(monitorExecutor.submit(Monitor,rootDir,pair,session, name,"voice","Sub", tcpVoiceSubMon,dtime,stopEvent))

        if localTesting:
            processes.append(Process(target=TestDataStreamFun, args=(numMuscles, numBlendshapes, numPriorities, datastreamHz, name, debug, stopEvent, tcpDataPub)))
            processes.append(Process(target=TestSubscriberFun, args=(debug, stopEvent, tcpDataSub)))
        else:
            processes.append(Process(target=DataStreamFun, args=(debug,streamerUDP_IP,streamerUDP_PORT,name, stopEvent, tcpDataPub)))
            processes.append(Process(target=SubscriberFun, args=(debug, localHostUDP_IP, subscriberUDP_PORT, numMuscles, checkbox_dict, stopEvent, tcpDataSub)))
        for process in processes:
            process.start()
        
        initEvent.set()


    def updateConnections(subscriber,outputDeviceIndex,audioRate,tcpVoiceSub):
        # print("Updating connections...")
        

        while not stopEvent.is_set():
            # start = timer()
            # event = subscriber.poll(timeout=10)
            # end = timer()
            # print(f'Duration: {(end - start)*1000}')
            # if event == 0:
            #     break
            # else:
            try:
                data = subscriber.recv_multipart(flags=zmq.NOBLOCK)
                connName = data[1]
                # print("procesing connection")
                if connName not in connections:
                    # print(f'Found new connection: {connName}')
                    connections.append(connName)
                    streams.append(createSubscriberStream(connName, connections, outputDeviceIndex, audioRate, tcpVoiceSub))
            except Exception as e:
                # print("Exhausted connections messages")
                break

            #print(connections)
        if not stopEvent.is_set():
            root.after(50,updateConnections,subscriber,outputDeviceIndex,audioRate, tcpVoiceSub)
        
    def disconnect(*args):
        if not stopEvent.is_set() and initEvent.is_set():
            print('Sending stop event')
            stopEvent.set()
            
            print('Stopping streams...')
            count = 1
            for stream in streams:
                print(count)
                count = count+1
                if stream.is_active():
                    stream.stop_stream()
                stream.close()
            #p.terminate()
            print('Waiting on processes to stop...')
            for process in processes:
                process.terminate()
                process.join()
            print('Getting monitor data...')
            results,notdone = wait(monitorFutures)
            for result in results:
                print(*result.result(),sep='\n')
            print('Stopping proxies...')
            print(f'There are {len(proxyCtrls)} proxies.')
            for ctrl,ctx in proxyCtrls:
                ctrl.send("TERMINATE".encode())
                ctx.destroy()
            proxyCtrls.clear()
            monitorFutures.clear()
            processes.clear()
            streams.clear()
            nonlocal context
            context.destroy()
            print("Disconnected...")


    def enumerateIODevices(*args):
        wasapiIndex = 2
        for api in range(p.get_host_api_count()):
            api_info = p.get_host_api_info_by_index(api)
            if api_info["type"] == pyaudio.paWASAPI:
                wasapiIndex = api
                break
        for index in range(p.get_device_count()):
            dev_dict = p.get_device_info_by_index(index)
            if dev_dict["maxInputChannels"] > 0 and dev_dict["hostApi"] == wasapiIndex:
                name = dev_dict["name"]
                desc = f'{name} - {dev_dict["defaultSampleRate"]}'
                inputDict[desc] = index
                inputRates[desc] = dev_dict["defaultSampleRate"]
                inputList.append(desc)
            if dev_dict["maxOutputChannels"] > 0 and dev_dict["hostApi"] == wasapiIndex:
                name = dev_dict["name"]
                desc = f'{name} - {dev_dict["defaultSampleRate"]}'
                outputDict[desc] = index
                outputList.append(desc)

    def on_checkbox_change(value,var):
        if(var.get()== True):
            checkbox_dict[value] = True
        else:
            checkbox_dict[value] = False

    def create_checkboxes(root, num_checkboxes):
        checkboxes = []
        for i in range(num_checkboxes):
            checkbox_var = tk.BooleanVar()
            checkbox = tk.Checkbutton(
                root,
                text=f"User {i+1}",
                variable=checkbox_var,
                command=lambda i = i, var=checkbox_var: on_checkbox_change(i+1,var)
            )
            checkbox.pack() 
    
    def processGuiInput() -> bool:
        nonlocal dtime
        nonlocal rootDir
        nonlocal inputDeviceIndex
        nonlocal outputDeviceIndex
        nonlocal audioRate
        nonlocal name
        nonlocal debug
        nonlocal localTesting
        nonlocal voiceLoopback
        nonlocal pair
        nonlocal session
        nonlocal streamerUDP_IP
        nonlocal streamerUDP_PORT
        nonlocal localHostUDP_IP
        nonlocal subscriberUDP_PORT
        nonlocal numMuscles
        nonlocal numBlendshapes
        nonlocal numPriorities
        nonlocal datastreamHz
        nonlocal address
        nonlocal portMultiple

        inputDeviceIndex = inputDict[selectedInput.get()]
        outputDeviceIndex = outputDict[selectedOutput.get()]
        audioRate = int(inputRates[selectedInput.get()])
        name = selectedUser.get()
        debug = debugVar.get() == 1
        localTesting = localTestingVar.get() == 1
        voiceLoopback = voiceLoopbackVar.get() == 1
        # logDir = dir_entry.get()
        pair = pair_entry.get().replace(' ','')
        session = session_entry.get().replace(' ','')
        streamerUDP_IP = ""
        streamerUDP_PORT = int(streamerUDPPort_entry.get())

        localHostUDP_IP = '127.0.0.1'
        subscriberUDP_PORT = int(subscriberUDPPort_entry.get())

        numMuscles = int(numMuscles_entry.get())
        numBlendshapes = int(numBlendshapes_entry.get())
        numPriorities = int(numPriorities_entry.get())
        datastreamHz = float(datastreamHz_entry.get())

        address = ARTNet_entry.get()
        portMultiple = userOptions.index(name)

        # check if we're in ARTNet/src, if not, ask for the ARTNet root directory location
        while rootDir.name != 'ARTNet':
            messagebox.showwarning(root,message="Could not identify the location of the ARTNet root directory. Please specify...")
            rootDir = Path(filedialog.askdirectory(mustexist=True))
        
        if selectedInput.get() == "":
            messagebox.showwarning(root,message="You must select an audio input before connecting")
            return False
        if selectedOutput.get() == "":
            messagebox.showwarning(root,message="You must select an audio output before connecting")
            return False
        try:
            p.is_format_supported(audioRate,
                                  input_device=inputDeviceIndex,
                                  input_channels= 2,
                                  input_format=pyaudio.paInt16
                                  )
            p.is_format_supported(audioRate,
                                  output_device=outputDeviceIndex,
                                  output_channels= 2,
                                  output_format=pyaudio.paInt16
                                  )
        except Exception as e:
            messagebox.showwarning(root, message="The selected pair of audio I/O devices do not have compatible sample rates. Please select a compatible pair or reconfigure devices in windows.")
            return False
        if pair == '':
            messagebox.showwarning(root, message="You must enter a pair name before connecting")
            return False
        
        if session == '':
            messagebox.showwarning(root, message="You must enter a session name before connecting")
            return False
        
        dtime = datetime.now().strftime('%H-%M-%S')

        #all good!
        return True
        
        


            
    # Create the main window
    root = tk.Tk()
    root.title("ARTNet GUI")

    num_checkboxes = 5
    checkbox_dict = {1: False, 2: False, 3: False, 4: False, 5: False}
    create_checkboxes(root, num_checkboxes)


    userOptions = ["User 1", "User 2", "User 3", "User 4", "User 5"]
    selectedUser = tk.StringVar()
    selectedUser.set("User 1")

    user_label = tk.Label(root, text="Select User")
    user_label.pack()
    userMenu = tk.OptionMenu(root, selectedUser, *userOptions)
    userMenu.pack()

    ARTNet_label = tk.Label(root, text="ARTNet Address")
    ARTNet_label.pack()
    ARTNet_entry = tk.Entry(root)
    ARTNet_entry.insert(0,'localhost')
    ARTNet_entry.pack()

    streamerUDPPort_label = tk.Label(root, text="Unreal Streamer UDP Port")
    streamerUDPPort_label.pack()
    streamerUDPPort_entry = tk.Entry(root)
    streamerUDPPort_entry.insert(0,'1234')
    streamerUDPPort_entry.pack()

    subscriberUDPPort_label = tk.Label(root, text="Unreal Subscriber UDP Port")
    subscriberUDPPort_label.pack()
    subscriberUDPPort_entry = tk.Entry(root)
    subscriberUDPPort_entry.insert(0,'7779')
    subscriberUDPPort_entry.pack()

    numMuscles_label = tk.Label(root, text="Number of Muscles")
    numMuscles_label.pack()
    numMuscles_entry = tk.Entry(root)
    numMuscles_entry.insert(0,'131')
    numMuscles_entry.pack()

    numBlendshapes_label = tk.Label(root, text="Number of Blendshapes")
    numBlendshapes_label.pack()
    numBlendshapes_entry = tk.Entry(root)
    numBlendshapes_entry.insert(0,'0')
    numBlendshapes_entry.pack()

    numPriorities_label = tk.Label(root, text="Number of Priorities")
    numPriorities_label.pack()
    numPriorities_entry = tk.Entry(root)
    numPriorities_entry.insert(0,'1')
    numPriorities_entry.pack()

    datastreamHz_label = tk.Label(root, text="Datastream Hz")
    datastreamHz_label.pack()
    datastreamHz_entry = tk.Entry(root)
    datastreamHz_entry.insert(0,'50')
    datastreamHz_entry.pack()

    apiDict = {}
    inputDict = {}
    inputList = []
    inputRates ={}
    outputDict = {}
    outputList = []
    enumerateIODevices()
    selectedInput = tk.StringVar()
    selectedOutput = tk.StringVar()
    
    input_label = tk.Label(root, text="Select Audio Input")
    input_label.pack()
    inputMenu = tk.OptionMenu(root, selectedInput, *inputList)
    inputMenu.pack()

    output_label = tk.Label(root, text="Select Audio Output")
    output_label.pack()
    outputMenu = tk.OptionMenu(root, selectedOutput, *outputList)
    outputMenu.pack()

    # audioRate_label = tk.Label(root, text="Audio Rate (Hz)")
    # audioRate_label.pack()
    # audioRate_entry = tk.Entry(root)
    # audioRate_entry.insert(0,'32000')
    # audioRate_entry.pack()

    debugVar = tk.IntVar()
    debug_button = tk.Checkbutton(root, text="Debug", variable=debugVar, onvalue=1, offvalue=0)
    debug_button.select()
    debug_button.pack()

    localTestingVar = tk.IntVar()
    localTesting_button = tk.Checkbutton(root, text="Local (Not Unreal) Testing", variable=localTestingVar, onvalue=1, offvalue=0)
    #localTesting_button.select()
    localTesting_button.pack()

    voiceLoopbackVar = tk.IntVar()
    voiceLoopback_button = tk.Checkbutton(root, text="Voice Loopback", variable=voiceLoopbackVar, onvalue=1, offvalue=0)
    #voiceLoopback_button.select()
    voiceLoopback_button.pack()

    # dir_label = tk.Label(root, text="Log Directory")
    # dir_label.pack()
    # dir_entry = tk.Entry(root)
    # dir_entry.insert(0,"")
    # dir_entry.pack()

    pair_label = tk.Label(root, text="Pair")
    pair_label.pack()
    pair_entry = tk.Entry(root)
    pair_entry.insert(0,'')
    pair_entry.pack()

    session_label = tk.Label(root, text="Session")
    session_label.pack()
    session_entry = tk.Entry(root)
    session_entry.insert(0,'')
    session_entry.pack()

    # dir_button = tk.Button(root, text="Select Directory", command=askDirectory)
    # dir_button.pack()

    # Create a connect button
    connect_button = tk.Button(root, text="Connect", command=connect)
    connect_button.pack()

    # Create a disconnect button
    disconnect_button = tk.Button(root, text="Disconnect", command=disconnect)
    disconnect_button.pack()

    root.bind('<Destroy>', disconnect)

    return root

def main():
    try:
        freeze_support()
        root = createPromptGUI()
        # Run the application
        root.mainloop()
        print('Exited Main Loop')
        print('Shutting Down')
    except Exception as e:
        print(e)
        while True:
            try:
                pass
            except KeyboardInterrupt:
                break
    

if __name__ == '__main__':
    main()