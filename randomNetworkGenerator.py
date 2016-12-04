import math
from igraph import *
from scipy.special import comb
import numpy as np
import pickle
import Crypto as crypto
from Crypto.Hash import HMAC
from Crypto import Random
import utility as util

def generate_random_wanet_mesh_graph(meshSize, classesNum, numByzantine, graphNodeSize = 40, fontSize = 14, sinkLocation = 0):

    # ===================================
    # Algorithm Parameters
    # ===================================

    color = ["#1abc9c", "#9b59b6", "#e74c3c", "#34495e", "#e74c3c", "#f1c40f", "#95a5a6"]

    # EBS Parameters
    m = 2 # Number of keys stored in each sensor
    k = 4 # number of keys stored in the head node
    EBSTable = []

    # building the graph
    #g = Graph.Tree(NSensors, maxChildren)
    g = Graph()
    meshGridSize = meshSize
    g.add_vertices(meshGridSize*meshGridSize)

    KS = []
    batteryInit = 2.0
    NSensors = meshGridSize*meshGridSize
    byzantineRate = int(numByzantine)

    # Security Layer Configuration
    SecurityBits = 16
    classes = classesNum

    # Plotting options

    bbox = (1000, 1000)
    layout = "grid"

    visual_style = {}
    visual_style["vertex_label_angle"] = 0
    visual_style["edge_width"] = 1
    visual_style["layout"] = layout
    visual_style["bbox"] = bbox
    visual_style["margin"] = 20

    # ===================================
    # Initialization
    # ===================================

    NodeIndexList = range(0,NSensors)

    for i in NodeIndexList:
        KS.append( crypto.Random.get_random_bytes(SecurityBits) )

    # ===================================
    # Uniformly random class assignments
    # ===================================
    # Generate equally likely class distribution for the whole network
    classAssignmentContainer = []
    classForEachNode = 1.0*NSensors/classes
    
    for i in range(0, classes):
        classAssignmentContainer.extend([i] * int(classForEachNode))
    
    if(len(classAssignmentContainer) != NSensors):
        for i in range(len(classAssignmentContainer), NSensors):
            randomClass = np.floor( np.random.uniform(0, classes, 1)).astype(np.int)[0]
            classAssignmentContainer.append(randomClass)
            
    classAssignmentContainer = np.random.choice(classAssignmentContainer, NSensors, replace=False).astype(np.int).tolist()
    
    # DEBUG::
    # print len(classAssignmentContainer)
    # print classAssignmentContainer
    
    # =======================================================
    # Building the graph and associate administrative keys
    # =======================================================

    graph_indices = {}
    randLayerColor = {}
    layerKey = {}

    for i in range(0,classes):
        graph_indices[i] = []
       
    # Initialize nodes with attributes
    for currentCell in range(0,NSensors):
        # Random class assignment
        g.vs[currentCell]["color"] = "white"
        
        # Reset energy variable foreach node
        g.vs[currentCell]["energy"] = 0.0
        g.vs[currentCell]["original_energy"] = 0.0
        
        g.vs[currentCell]["connection"] = []
        
        
    # Generate Mesh Grid
    for i in range(0,meshGridSize):
        for j in range(0,meshGridSize):

            currentCell = i+(j*meshGridSize)
            
            graph_indices[classAssignmentContainer[currentCell]].append(currentCell)
            
            if(i<meshGridSize-1):
                g.add_edge(currentCell,currentCell+1)
                g.vs[currentCell]["connection"].append(currentCell+1)
                g.vs[currentCell+1]["connection"].append(currentCell)
                
            if(j<meshGridSize-1):
                g.add_edge(currentCell,currentCell+meshGridSize)
                g.vs[currentCell]["connection"].append(currentCell+meshGridSize)
                g.vs[currentCell+meshGridSize]["connection"].append(currentCell)
                
            if(j<meshGridSize-1 and i<meshGridSize-1):
                g.add_edge(currentCell,currentCell+1+meshGridSize)
                g.vs[currentCell]["connection"].append(currentCell+1+meshGridSize)
                g.vs[currentCell+1+meshGridSize]["connection"].append(currentCell)
                
            if(j<meshGridSize-1 and i>0):
                g.add_edge(currentCell,currentCell-1+meshGridSize)
                g.vs[currentCell]["connection"].append(currentCell-1+meshGridSize)
                g.vs[currentCell-1+meshGridSize]["connection"].append(currentCell)
                

    # Random Byzantine node
    byzantineIndices = np.random.choice(range(1, NSensors), byzantineRate, replace=False).astype(np.int).tolist()
            
    # Assign keys and color for layers
    for i in range(0,classes):
        # Generate a distinct color for each node belongs to a layer
        randLayerColor[i] = color[i%len(color)]
        # Generate layer keys for later assignement
        layerKey[i] = crypto.Random.get_random_bytes(SecurityBits)

    # assign classes to graph vertices
    for layer in range(0,classes):
        for i in graph_indices[layer]:
            g.vs[i]["label"] = "C"+str(layer+1)+"\n"+str(i)
            g.vs[i]["layer"] = layer
            g.vs[i]["SKey"] = KS[i]
            g.vs[i]["msg"] = ""
            g.vs[i]["LKey"] = layerKey[layer]
            g.vs[i]["color"] = randLayerColor[layer]

    # assign random byzantine nodes
    for i in byzantineIndices:
        g.vs[i]["label"] = "C"+str(g.vs[i]["layer"]+1)+"\n"+str(i)
        g.vs[i]["color"] = "black"
        g.vs[i]["label_color"] = "white"

    g.vs["size"] = graphNodeSize
    g.vs["label_size"] = fontSize

    # Style the Fusion Center
    g.vs[sinkLocation]["size"] = graphNodeSize
    g.vs[sinkLocation]["color"] = "red"

    # Plot the graph
    layout = g.layout(layout)
    #image = plot(g, **visual_style)
    #image.save("graph.png");
    
    # ==========================================================
    # Iterative Message transmission from source to destination
    # ==========================================================

    # output = open('myfile'+str(meshSize)+'-'+str(classesNum)+'.pkl', 'wb')
    # pickle.dump(g, output)
    # output.close()
    
    return g


# meshSize = 5
# numClasses = [3]
# numMessages = [1]
# numHops = [25000]
# #numHops = [10]
# mobility = True
# saveMode = False

# g = generate_random_wanet_mesh_graph(meshSize, 3, 4, 40, 12)
# # Plot the graph
# layout = g.layout(layout)
# image = plot(g, **visual_style)
# image.save("savedgraph.png")meshSize = 5
# numClasses = [3]
# numMessages = [1]
# numHops = [25000]
# #numHops = [10]
# mobility = True
# saveMode = False

# g = generate_random_wanet_mesh_graph(meshSize, 3, 4, 40, 12)

# bbox = (1000, 1000)
# layout = "grid"

# visual_style = {}
# visual_style["vertex_label_angle"] = 0
# visual_style["edge_width"] = 1
# visual_style["layout"] = layout
# visual_style["bbox"] = bbox
# visual_style["margin"] = 20

# # Plot the graph
# layout = g.layout(layout)
# image = plot(g, **visual_style)
# image.save("savedgraph.png")