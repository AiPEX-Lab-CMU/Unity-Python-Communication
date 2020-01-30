#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq
import sys
import numpy as np
import io
from scipy import misc
import os
import imageio
from stl import mesh
import matplotlib.pyplot as plt
from PIL import Image
import datetime
import argparse
import threading
import json

print("python server started")
parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true', default = False,
                    dest='simple_value', help='Print information when receiving data')

result = parser.parse_args()

carWaitTime = {}

#The dataset containing the data collected from Unity
simulationDataset = []

def receiveData():
    global result
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    totalTime = 0.0
    averageTime = 0.0
    number = 0.0
    verbose = result.simple_value
    while True:
        #  Wait for next request from client
        message = socket.recv()
        data_type = message[0:3].decode('utf-8')
        socket.send("Message Received".encode('utf-8'))
        currentTime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
        #Image
        if data_type == "000":
            picName = "./snapshots/" + currentTime + ".jpg"
            with open(picName, "wb") as f:
                f.write(message[3:])
            if verbose:
                matrix = imageio.imread("1.jpg")
                print("Matrix with shape of %s" %(matrix.shape,))
                print(matrix)
                im = Image.open("1.jpg")
                im.show()
                plt.imshow(matrix)
        elif data_type == "001":
            #plaintext
            content = message[3:].decode('utf-8')
            receipt = {}
            receipt['items'] = {}
            receipt['Unavailable Items'] = 0
            receipt['Time Spent'] = 0.0
            parseItems = content.split('\n')
            items = parseItems[0].split('\t')[1:]
            for item in items:
                if item in receipt['items']:
                    receipt['items'][item] += 1
                else:
                    receipt['items'][item] = 1
            receipt['Unavilable Items'] = int(parseItems[1])
            receipt['Time Spent'] = float(parseItems[2])
            json_data = json.dumps(receipt)
            simulationDataset.append(json_data)
            if verbose:
                print(json_data)
            #plaintextName = "./plaintext/" + currentTime + ".txt"
            #with open(plaintextName, "wb") as f:
                #f.write(content)
            #if verbose:
                #print(content)
        elif data_type == "002":
            #point cloud
            objName = "./pointCloud/" + currentTime + ".obj"
            with open(objName, "wb") as f:
                f.write(message[11:])
            with open(objName, "r") as f:
                lines = f.readlines()
            if verbose:
                vertices = []
                for line in lines:
                    if len(line) > 0:
                        arguments = line.split(' ')
                        if len(arguments) == 4 and arguments[0] == "v":
                            vertices.append([float(arguments[1]), float(arguments[2]), float(arguments[3])])
                print(vertices)
        elif data_type == "003":
            #time waiting for traffic light
            waitTime = message[3:].decode('utf-8').split('#')
            if verbose:
                print(message[3:].decode('utf-8'))
            carID = waitTime[0]
            global carWaitTime
            if carID not in carWaitTime:
                carWaitTime[carID] = []
            carWaitTime[carID].append((waitTime[1], waitTime[2], float(waitTime[3])))
        elif data_type == "End":
            print("Exiting")
            time.sleep(3)
            sys.exit()

receiveData()

#TODO: Write your code here