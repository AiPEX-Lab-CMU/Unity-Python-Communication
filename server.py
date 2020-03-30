#
#   Binds REP socket to tcp://*:5555
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
import random

print("python server started")
parser = argparse.ArgumentParser()

parser.add_argument('-v', '--verbose', action='store_true', default = False,
                    dest='simple_value', help='Print information when receiving data')

result = parser.parse_args()

carWaitTime = {}

nameTranslator = {}

#The dataset containing the data collected from Unity, it will be filled with
#data after calling receiveData, which blocks until the simulation is completed
simulationDataset = []

#This dictionary contains the prices for the different goods, use if after
#receiveData() to lookup prices for items
itemPrices = {}

#Initialize names and prices of items to be filled with essential information
def initializeItems():
    with open("items.txt", 'r') as item:
        for lineRaw in item:
            line = lineRaw.rstrip().split(' ')
            nameTranslator[line[0]] = line[1]
    with open('prices.txt', 'r') as price:
        for lineRaw in price:
            line = lineRaw.rstrip().split(' ')
            itemPrices[line[0]] = round(float(line[1]), 2)
    for _key, value in nameTranslator.items():
        if value not in itemPrices:
            print("Item is missing")
            print(value) 

#Print receipt in understandable format
def printReceipt(receipt):
    global itemPrices
    print("------Welcome to the Supermarket------")
    print("Items in Cart:")
    for key,value in receipt['Items'].items():
        print("   " + key+' '*(17 - len(key))+str(value)+'x'+str(itemPrices[key]))
    print("Unavailable Items:")
    for key,value in receipt['Unavailable Items'].items():
        print("   " + key+' '*(17 - len(key))+str(value))
    print("Total Price:"+ ' ' * 12 + str(receipt['Total Price']))
    print("Time Spent Waiting:" + ' ' * 12 + str(receipt['Time Spent']))
    print("-----------Have a nice day!-----------\n")

def handlePicture(message, currentTime, socket):
    global result
    verbose = result.simple_value
    picName = "./snapshots/" + currentTime + ".jpg"
    with open(picName, "wb") as f:
        f.write(message[3:])
    if verbose:
        matrix = imageio.imread(picName)
        print("Matrix with shape of %s" % (matrix.shape,))
        print(matrix)
        im = Image.open(picName)
        im.show()
        plt.imshow(matrix)
    #TODO: Replace the line below with your own algorithm to determine if products need to be restocked, still the final result will need to be a boolean named restock to determine if items need to restocked or not
    restock = random.choice([True, False]) 
    option = "True" if restock else "False"
    socket.send(option.encode('utf-8'))

def handlePointCloud(message, currentTime):
    global result
    verbose = result.simple_value
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

def writeToFile(simulationDataset):
    f = open('output.txt', 'w')
    for (index, data) in enumerate(simulationDataset):
        entry = ""
        entry += str(index)
        entry += " "
        for key, val in data['Items'].items():
            for _i in range(val):
                entry += key
                entry += ","
        if data['Left Early']:
            entry += "Left out of frustration"
            entry += ","
        entry = entry[:-1]
        entry += " "
        entry += str(data['Time Spent'])
        entry += "\n"
        f.write(entry)
    f.close()



#Communicate with Python to fetch data
def receiveData():
    global nameTranslator
    global result
    global itemPrices
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    totalTime = 0.0
    averageTime = 0.0
    number = 0.0
    verbose = result.simple_value
    totalRevenue = 0.0
    totalWaitingTime = 0.0
    if not os.path.isdir("./snapshots/"):
        os.mkdir("./snapshots/")
    while True:
        #  Wait for next request from client
        message = socket.recv()
        data_type = message[0:3].decode('utf-8')
        if data_type != "000":
            socket.send("Message Received".encode('utf-8'))
        currentTime = str(int(time.time()*100))
        #Image
        if data_type == "000":
            handlePicture(message, currentTime, socket)
        elif data_type == "001":
            #plaintext
            content = message[3:].decode('utf-8')
            if content.startswith('Frustrated'):
                print(content)
                continue
            receipt = {}
            receipt['Items'] = {}
            receipt['Total Price'] = 0.0
            receipt['Time Spent'] = 0.0
            receipt['Left Early'] = False
            parseItems = content.split('\n')
            items = parseItems[0].split('\t')
            items.pop(0)
            for item in items:
                if item == "Frustrated":
                    receipt['Left Early'] = True
                    continue
                correctName = nameTranslator[item]
                if correctName in receipt['Items']:
                    receipt['Items'][correctName] += 1
                else:
                    receipt['Items'][correctName] = 1
                receipt['Total Price'] += itemPrices[correctName]
            receipt['Total Price'] = round(receipt['Total Price'], 2)
            totalRevenue += receipt['Total Price']
            receipt['Unavailable Items'] = {}
            unavailableItems = parseItems[1].split('\t')
            unavailableItems.pop(0)
            for item in unavailableItems:
                correctName = nameTranslator[item]
                if correctName in receipt['Unavailable Items']:
                    receipt['Unavailable Items'][correctName] += 1
                else:
                    receipt['Unavailable Items'][correctName] = 1
            receipt['Time Spent'] = round(float(parseItems[2]), 2)
            totalWaitingTime += receipt['Time Spent']
            if verbose:
                printReceipt(receipt)
            json_data = json.dumps(receipt)
            simulationDataset.append(receipt)
            #plaintextName = "./plaintext/" + currentTime + ".txt"
            #with open(plaintextName, "wb") as f:
                #f.write(content)
            #if verbose:
                #print(content)
        elif data_type == "002":
            handlePointCloud(message, currentTime)
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
            break
    writeToFile(simulationDataset)
    print("Total Revenue: %.2f" %(round(totalRevenue,2),))
    print("Total Waiting Time: %.2f" %(round(totalWaitingTime,2),))

def main():
    initializeItems()
    receiveData()
    #TODO: Write your code here

if __name__ == "__main__":
    main()
