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

print("python server started")
parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true', default = False,
                    dest='simple_value', help='Print information when receiving data')

result = parser.parse_args()

carWaitTime = {}

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
            plaintextName = "./plaintext/" + currentTime + ".txt"
            with open(plaintextName, "wb") as f:
                f.write(content)
            if verbose:
                print(content)
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
            #millisecondsElapsed = float(message[3:].decode('utf-8'))
            #print("Time elapsed is %f milliseconds" %(millisecondsElapsed))
            #totalTime += millisecondsElapsed * 1.0
            #number += 1.0
            #averageTime = totalTime / number
            #print("Average time elapsed is %f milliseconds" %(averageTime))
        elif data_type == "End":
            print("Exiting")
            time.sleep(3)
            sys.exit()


def interact():
    while True:
        global carWaitTime
        command = input(">> ")
        if command == "exit":
            sys.exit()
        args = command.split(" ")
        if len(args) != 3:
            print("Error: Invalid command")
            continue
        if args[0] == "show":
            if args[1] == "trafficlight":
                if args[2] == "all":
                    for key, value in carWaitTime.items():
                        print(key)
                else:
                    if args[2] in carWaitTime:
                        print(carWaitTime[args[2]])

threads = []
t1 = threading.Thread(target = receiveData)
t2 = threading.Thread(target = interact)
threads.append(t1)
threads.append(t2)
t1.start()
t2.start()
t1.join()
t2.join()
