import pickle, string, sys, math
from igraph import *
import numpy as np
import matplotlib.pyplot as plt
from random import *
import utility as util

######################### Input ################33
## graph        => Contains the generated network mesh-grid as graph
## classes      => Defines the number of segments (Groups) the network (graph) has 
## meshGridSize => Defines the GridSize as square root value of the entier network size
## numberHops   => Use it to define how many routing hops the communication message should traverse 
## sinkLocation => Define the master node location using the node ID (0 represent the top left node)

def RecursiveRandomRouting(graph, classes, meshGridSize, numberHops, sinkLocation = 0):
    # Random scr/dest selection
    # Select non-byzantine source
    
    # Calculate how many bytes required to index the whole sensor from [0,N]
    indexRequiredBytes = math.log(meshGridSize**2, 2)
    indexRequiredBytes = math.ceil(indexRequiredBytes/8.0)
    
    bitsRequiredForClasses = math.ceil(math.log(classes, 2))
    
    src = randint(1,(meshGridSize**2)-1)
    # src = 7
    
    while graph.vs[src]["color"]=="black":
        src = randint(1,(meshGridSize**2)-1)
            
    # Initialize message complixty variable to hold the size and number of messages used along a single DFD route
    messageComplexity = []
    originalMessageComplexity = []
    recordEnergyConsumption = []
    recordEnergyConsumptionWithoutDFD = []

    # Generate a random walk path to the sink (sinkLocation=0 Default)
    route = util.GenerateRandomPath(graph,src,meshGridSize)
    # route = util.random_walk_route(graph, src, sinkLocation, numberHops)

    # Color routes with blue color
    for idx, i in enumerate(route):
        # Color edges differently between byzantine candidates
        if(idx < len(route)-1):
            eid = graph.get_eid(route[idx],route[idx+1])
            graph.es[eid]["color"] = "blue"

    # Initialize the entry source message
    msg = {"msg":"hello", "dest":sinkLocation, "src":src, "byzantineNodeDict":[], "healthyNodes":[]}
    
    # Initial message complexity would be the number of message bytes + (dest+src)(bytes)
    initialMessageComplexity = len(msg["msg"])+indexRequiredBytes+2*indexRequiredBytes
    messageComplexity.append(initialMessageComplexity);
    
    # Update source node with the initial message
    graph.vs[route[0]]["msg"] = msg

    # reset hashes to empty strings [hash0, hash1, ..., hashN]
    for i in range(0,classes):
        msg["hash"+str(i)] = ""

    healthyNodeDict = []
    byzNodes = []
    counter = 0

    # DFD Entry Point
    # Start routing messages from source to the destination
    for currentNodeIndx in route:

        # Intercept the message from the previous node and extract information from it
        passedMsg = graph.vs[currentNodeIndx]["msg"]
        currentNodeClass = graph.vs[currentNodeIndx]["layer"]
        currentNodeKey = graph.vs[currentNodeIndx]["LKey"]

        # print "Node ("+str(currentNodeIndx)+") Layer ("+str(currentNodeClass)+")"

        # If this is the source node then apply MAC and update and forward the message accordingly
        # ===================================================================
        # =================== Source Node ============
        # ===================================================================
        if(currentNodeIndx==route[0]):
            passedMsgNewMAC = util.MAC_message(passedMsg["msg"]+str(passedMsg["dest"])+str(passedMsg["src"]), currentNodeKey)
            passedMsg["hash"+str(currentNodeClass)] = passedMsgNewMAC
            #passedMsg["lastHasher"+str(currentNodeClass)] = currentNodeIndx
            passedMsg["trackHopClasses"] = [currentNodeClass]
            passedMsg["trackHops"] = [currentNodeIndx]
        
        # If not the source node and the destination node then enter verification mode
        # ===================================================================
        # =================== Intermediate routing nodes ============
        # ===================================================================
        if(currentNodeIndx!=route[0] and currentNodeIndx != 0):
            util.verify_data_integrity(passedMsg, currentNodeClass, currentNodeKey, currentNodeIndx, byzNodes, graph)
            
        # ===================================================================
        # =================== Last node ============
        # ===================================================================
        if(currentNodeIndx==0):
            # Use fusion center as last checker, and in case byzantine node identified just break
            for nodeClass in range(0,classes):
                if util.verify_data_integrity(passedMsg, nodeClass, currentNodeKey, currentNodeIndx, byzNodes, graph, True):
                    break
                    
        # print passedMsg

        # If Byzantine node apply an attack to the message
        if(graph.vs[currentNodeIndx]["color"]=="black"):
            passedMsg["msg"] = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(len(passedMsg["msg"])))

        if(counter+1<len(route)):
            # Pass the message to the next hub
            msgComplexityInBits = util.CalculateMessageComplexity(indexRequiredBytes, bitsRequiredForClasses, passedMsg, classes)
            
            # Handle power consumption
            recordEnergyConsumption.append(util.consume_receive_energy_from_node(graph, currentNodeIndx, msgComplexityInBits))
            recordEnergyConsumptionWithoutDFD.append(util.consume_receive_original_energy_from_node(graph, currentNodeIndx, initialMessageComplexity*8.0))
            
            convertedToBytes = math.ceil(msgComplexityInBits/8.0)
            messageComplexity.append(convertedToBytes+initialMessageComplexity)
            
            graph.vs[route[counter+1]]["msg"] = dict(passedMsg)
            
            # Clear message from previous node to avoid multi-route test conflict
            graph.vs[route[counter]]["msg"] = {}
        else:
            # Plot message complexity
            # plt.plot(messageComplexity)
            # plt.title("Message Complexity")
            # plt.xlabel("Value")
            # plt.ylabel("Message Size")
            # plt.show()
            break
        
        recordEnergyConsumption.append(util.consume_transmission_energy_from_node(graph, currentNodeIndx, msgComplexityInBits))
        recordEnergyConsumptionWithoutDFD.append(util.consume_transmission_original_energy_from_node(graph, currentNodeIndx, initialMessageComplexity*8.0))
        # increment
        counter=counter+1

    # Return the number of communication sent and the total size of messages
    return byzNodes, passedMsg["healthyNodes"], passedMsg["byzantineNodeDict"], messageComplexity, len(route), recordEnergyConsumption, recordEnergyConsumptionWithoutDFD

