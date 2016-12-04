import sys
import binascii
from igraph import *
from random import randint, choice
from Crypto.Hash import HMAC
from itertools import islice, takewhile

def consume_transmission_energy_from_node(graph, nodeIndex, bits):
    """
    Function that will be used to calculate the transmission power consumption for every message transfer
    The Energy Consumption Model is based on :
    E_tx =E_tx_amp+E_tx_elec
    E_rx = R_rx_elec 
    http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=1045297&tag=1

    :param graph: Graph based on iGraph framework
    :param nodeIndex: iGraph vertex index (Grarph.vs[index])
    
    :returns: This function will deduct energy from initial overall energy stored for each node in Joule and store it back to the original Graph
    :raises keyError: Energy consumption failure
    """
    # Predefined static distance between node as an assumption is 2 meters
    d = 2
    
    # The electronic energy (50 nJ / bit)
    E_elec = 50e-9 * bits
    # The free space energy parameter
    E_fs = 10e-12
    # Amplifier energy (50 pJ / bit / m^2)
    E_amp = E_fs * d**2 * bits
    
    comulativeEnergyDissipation = graph.vs[nodeIndex]["energy"]
    comulativeEnergyDissipation += (E_amp + E_elec)*1.0
    graph.vs[nodeIndex]["energy"] = comulativeEnergyDissipation
    
    return comulativeEnergyDissipation
    
def consume_receive_energy_from_node(graph, nodeIndex, bits):
    """
    Function that will be used to calculate the receive power consumption for every message transfer
    The Energy Consumption Model is based on :
    E_tx =E_tx_amp+E_tx_elec
    E_rx = R_rx_elec 
    http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=1045297&tag=1

    :param graph: Graph based on iGraph framework
    :param nodeIndex: iGraph vertex index (Grarph.vs[index])

    :returns: This function will deduct energy from initial overall energy stored for each node in Joule 
    :raises keyError: Energy consumption failure
    """ 
    # The electronic energy (50 nJ / bit)
    E_elec = 50e-9 * bits
    
    comulativeEnergyDissipation = graph.vs[nodeIndex]["energy"]
    comulativeEnergyDissipation += (E_elec*1.0)
    graph.vs[nodeIndex]["energy"] = comulativeEnergyDissipation
    
    return comulativeEnergyDissipation
    
def consume_transmission_original_energy_from_node(graph, nodeIndex, bits):
    """
    Function that will be used to calculate the transmission power consumption for every message transfer
    The Energy Consumption Model is based on :
    E_tx =E_tx_amp+E_tx_elec
    E_rx = R_rx_elec 
    http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=1045297&tag=1

    :param graph: Graph based on iGraph framework
    :param nodeIndex: iGraph vertex index (Grarph.vs[index])
    
    :returns: This function will deduct energy from initial overall energy stored for each node in Joule and store it back to the original Graph
    :raises keyError: Energy consumption failure
    """
    # Predefined static distance between node as an assumption is 2 meters
    d = 2
    
    # The electronic energy (50 nJ / bit)
    E_elec = 50e-9 * bits
    # The free space energy parameter
    E_fs = 10e-12
    # Amplifier energy (50 pJ / bit / m^2)
    E_amp = E_fs * d**2 * bits
    
    comulativeEnergyDissipation = graph.vs[nodeIndex]["original_energy"]
    comulativeEnergyDissipation += (E_amp + E_elec)*1.0
    graph.vs[nodeIndex]["original_energy"] = comulativeEnergyDissipation
    
    return comulativeEnergyDissipation
    
def consume_receive_original_energy_from_node(graph, nodeIndex, bits):
    """
    Function that will be used to calculate the receive power consumption for every message transfer
    The Energy Consumption Model is based on :
    E_tx =E_tx_amp+E_tx_elec
    E_rx = R_rx_elec 
    http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=1045297&tag=1

    :param graph: Graph based on iGraph framework
    :param nodeIndex: iGraph vertex index (Grarph.vs[index])

    :returns: This function will deduct energy from initial overall energy stored for each node in Joule 
    :raises keyError: Energy consumption failure
    """ 
    # The electronic energy (50 nJ / bit)
    E_elec = 50e-9 * bits
    
    comulativeEnergyDissipation = graph.vs[nodeIndex]["original_energy"]
    comulativeEnergyDissipation += (E_elec*1.0)
    graph.vs[nodeIndex]["original_energy"] = comulativeEnergyDissipation
    
    return comulativeEnergyDissipation
    
def random_walk_iter(g, start=None): 
    current = randint(0, g.vcount()-1) if start is None else start 
    while True: 
        yield current
        current = choice(g.successors(current))

# FIX: There is a problem here. To simulate Random Walk routing properly we need to exclude previous node from routing
def random_walk_route(g, start, finish, desired_length):
    walk = list(islice(random_walk_iter(g, start), desired_length))
    
    return walk

def MAC_message(msg, key):
    msgMAC = HMAC.HMAC(key, msg)
    
    return msgMAC.hexdigest()

# Apply Random Mobility
def random_mobility(g, size):
    
    for i in range(1, size):
        randIdx1 = i
        randIdx2 = randint(1,size-1)

        tmpConnectionIndx1 = []
        tmpConnectionIndx2 = []
        
        # Unlink node 1 & connect node 2
        for edge in g.vs[randIdx1]["connection"]:
            id = g.get_eid(randIdx1, edge)
            g.delete_edges(id)
            
            # remove randIdx1 edge from edge and vice versa 
            g.vs[edge]["connection"].remove(randIdx1)
            
            # Link edge to the second node
            g.add_edge(edge, randIdx2)
            g.vs[edge]["connection"].append(randIdx2)
            if edge != randIdx2:
                tmpConnectionIndx2.append(edge)
            else:
                # randIdx1 is my neighbour
                tmpConnectionIndx2.append(randIdx1)
        
        # Clear node1 connection list
        g.vs[randIdx1]["connection"] = []
        
        # Unlink node 2 & connect node 1
        for edge in g.vs[randIdx2]["connection"]:
            id = g.get_eid(randIdx2, edge)
            g.delete_edges(id)
            
            # remove randIdx1 edge from edge and vice versa 
            g.vs[edge]["connection"].remove(randIdx2)
            
            # Link edge to the first node
            g.add_edge(edge, randIdx1)
            g.vs[edge]["connection"].append(randIdx1)
            g.vs[randIdx1]["connection"].append(edge)
        
        # Finally move tempList of edges to node 2
        g.vs[randIdx2]["connection"] = tmpConnectionIndx2
    
    return g

def plot_save_graph(graph, savefilename, healthyNodes = False, boldLines = True):
    # Plotting options
    bbox = (1000, 1000)
    layout = "grid"
    
    visual_style = {}
    visual_style["vertex_label_angle"] = 0
    visual_style["edge_width"] = 1
    visual_style["layout"] = layout
    visual_style["bbox"] = bbox
    visual_style["margin"] = 20
    
    if boldLines:
        # If edge color is red, then increase line size
        visual_style["edge_width"] = [(4 if color=="red" else 6 if color=="blue" else 1) for color in graph.es["color"]]
    if healthyNodes != False:
        for i in healthyNodes:
            if(i!=0):
                graph.vs[i]["shape"] = "triangle"
                pass
    
    # Plot the graph
    layout = graph.layout(layout)
    image = plot(graph, **visual_style)
    image.save(savefilename)

    pass
    
# Get the size of dictionary
def GetDictSize(dict):
    non_mem_macs_len = 0
    for idx in dict:
        non_mem_macs_len += len(binascii.hexlify(str(idx)))
        non_mem_macs_len += len(binascii.hexlify(str(dict[idx])))
    return non_mem_macs_len

# Calculate message complexity
def CalculateMessageComplexity(indexRequiredBytes, bitsRequiredForClasses, passedMsg, classes):
    hashSize = 16
    complexityInBits = 0
    for idx in passedMsg:
        # Check if hash is not filled then don't include it in the message size
        if("hash" in idx):
            for c in range(0,classes):
                if("hash"+str(c) == idx and len(passedMsg["hash"+str(c)])>0 ):
                    complexityInBits += hashSize
        elif("healthy" in idx):
            complexityInBits += len(passedMsg["healthyNodes"])*indexRequiredBytes*8.0
        elif("byzantineNode" in idx):
            # complexityInBits += len(passedMsg["byzantineNodeDict"])*indexRequiredBytes*8.0
            complexityInBits += len(passedMsg["byzantineNodeDict"])*indexRequiredBytes*8.0
        elif("trackHopClasses" in idx):
            complexityInBits += len(passedMsg["trackHopClasses"])*bitsRequiredForClasses
        elif("trackHops" in idx):
            complexityInBits += len(passedMsg["trackHops"])*indexRequiredBytes*8.0
            
    return complexityInBits

# Generate 4 random route direction. Vertical, Horizontal, Diagonal and Zigzag Diagonal
def GenerateRandomPath(graph, source, meshGridSize, sinkLocation = 0 ):
    x=y=0
    up = left = True
    path = [source]
    currentCell = source
    vsCount = len(graph.vs)

    # Select random walk type
    randWay = randint(0,4)

    if(randWay==0):
        # Horizontal
        y = -1
    elif(randWay==1):
        # Vertical
        x = -1
    elif(randWay==2):
        # Diagonal Zigzag
        x=y=-1
    else:
        # Diagonal
        return graph.get_shortest_paths(source,0)[0]

    # Start generating steps and update path list
    for i in range(0,meshGridSize**2):
        if(currentCell + (y*meshGridSize)>=0 and y!=0):
            # Move up
            currentCell = currentCell + (y*meshGridSize)
            path.append(currentCell)
        else:
            up = False

        if(currentCell + (x) >= (math.floor(currentCell*1.0/meshGridSize)*meshGridSize) and x!=0):
            # Move left
            currentCell = currentCell + (x)
            path.append(currentCell)
        else:
            left = False

        # Exit if there is no more steps to take
        if(up == False and left == False):
            break

    if(currentCell!=sinkLocation):
        if(currentCell<meshGridSize):
            for i in range(currentCell-1, -1, -1):
                path.append(i)
        else:
            for i in range(currentCell-meshGridSize, -1, -meshGridSize):
                path.append(i)

    return path

# This function takes the current routing node and identify faulty nodes based on its class
# The function returns how many steps it went backward to build the byzantine candidate list
# And it returns the starting point from where the Byzantine candidate list should start
def fault_label_intermediate_nodes(passedMsg, currentNodeClass, previousNodeClass):
    # these two variables will be used to select range of candidate byzantine from trackHops array
    byzStart = -1
    steps = 0
            
    for indx in range(len(passedMsg["trackHops"])-2,-1,-1):
        # print "Step: " + str(passedMsg["trackHops"][indx])
        steps = steps + 1
        # If backtrack steps are above 4, it is too expensive to count
        if(steps>4): return -2,0
        if(passedMsg["trackHopClasses"][indx]==currentNodeClass):
            # Add 1 and don't include the first class we compare with
            byzStart = indx
            break

    # If there is conflict and the previous node does have the same class, tag the previous node as byzantine
    if(steps == 1 and (currentNodeClass==previousNodeClass[0])):
        byzStart -= 1
        steps += 1
        
    # Debug
    #print "startindx :"+str(byzStart)
    #print "endindx :"+str(byzStart+steps)
    #print passedMsg["trackHops"]
    
    return byzStart, steps
   
# Return a list of clean nodes
def white_label_intermediate_nodes(passedMsg, currentNodeClass, previousNodeClass):
    # Path is clear 
    # if(len(passedMsg["byzantineNodeDict"])==0):
    #     return passedMsg["trackHops"][1:-1]
    # else:
    # these two variables will be used to select range of candidate byzantine from trackHops array
    start = -1
    steps = 0
    healthyCandidates = []
        
    for indx in range(len(passedMsg["trackHops"])-2,-1,-1):
        steps = steps + 1

        if(passedMsg["trackHopClasses"][indx]==currentNodeClass):
            # Add 1 and don't include the first class we compare with
            start = indx
            break

    if(start!=-1):
        healthyCandidates = passedMsg["trackHops"][start+1:start+steps]
    
    return healthyCandidates

def verify_data_integrity(passedMsg, currentNodeClass, currentNodeKey, currentNodeIndx, byzNodes, graph, FC = False, memory_storage = False):
    # Check if same hash exist
    passedMAC = passedMsg["hash"+str(currentNodeClass)]
    #lastHasher = passedMsg["lastHasher"+str(currentNodeClass)]
    
    # Create another hash regardless
    passedMsgNewMAC = MAC_message(passedMsg["msg"]+str(passedMsg["dest"])+str(passedMsg["src"]), currentNodeKey)

    # If mac from similar class is empty, update it
    if(passedMAC == ""):
        # Register last hasher/hash
        passedMsg["hash"+str(currentNodeClass)] = passedMsgNewMAC
        #passedMsg["lastHasher"+str(currentNodeClass)] = currentNodeIndx
    
    previousNodeClass = passedMsg["trackHopClasses"][-1:]
    # Finalize DFD algorithm at the Fusion center, or the destination node
    # If we reach FC stop counting hops and hop classes as we don't need that
    passedMsg["trackHopClasses"].append(currentNodeClass)
    passedMsg["trackHops"].append(currentNodeIndx)

    # Verification process
    if(passedMAC != ""):
        report = {}
        
        # If there was a MAC conflict between same classes
        if(passedMsg["hash"+str(currentNodeClass)] != passedMsgNewMAC):
            
            # iterate through recorded hops and fetch intermediate nodes trapped between the current node class
            byzStart, steps = fault_label_intermediate_nodes(passedMsg, currentNodeClass, previousNodeClass)

            if(byzStart!=-1 and byzStart!=-2):
                byzCandidates = passedMsg["trackHops"][byzStart+1:byzStart+steps]
                # Apply MAC and forward the msg to the next node
                report["reporter"] = currentNodeClass
                report["byz"] = byzCandidates
                # report["class"] = currentNodeClass
                if(len(byzCandidates)>0):
                    # DEBUG:: passedMsg["byzantineNodeDict"].append((currentNodeClass, currentNodeIndx, byzCandidates))
                    
                    # If memory storage is enabled
                    if memory_storage:
                        # Check if this discovery is an old existing one for the current node
                        # In case the discovery is old, discard adding it to the passedMsg
                        for candidate in byzCandidates:
                            if candidate in graph.vs[currentNodeIndx]["found_byz"]:
                                byzCandidates.remove(candidate)
                        
                    # ==== Message size optimization ====
                    # Make sure there is no redundant faulty nodes are been reported
                    # Check for faulty node indices, and if they are distinct report them
                    for candidate in byzCandidates:
                        if(candidate not in passedMsg["byzantineNodeDict"] and candidate not in passedMsg["healthyNodes"]):
                            passedMsg["byzantineNodeDict"].append(candidate)
                            
                            if memory_storage:
                                # Update current node memory with the discovery
                                graph.vs[currentNodeIndx]["found_byz"].append(candidate)

                # Build clean list of identified byzantine nodes with repetition
                for idx, i in enumerate(byzCandidates):
                    # Reset previous hop hashes to ignore them in onward verification
                    #passedMsg["hash"+str(graph.vs[i]["layer"])] = ""

                    # Change the shape of identified Byzantine nodes for easier visualization
                    if i!=0:
                        graph.vs[i]["shape"] = "rectangle"
                        byzNodes.append(i)
                    # Color edge differently between byzantine candidates
                    # if(idx < len(byzCandidates)-1):
                    #     eid = graph.get_eid(byzCandidates[idx],byzCandidates[idx+1])
                    #     graph.es[eid]["color"] = "red"
                
                # Only if faults have been caught
                # Change the hash to stop the fault from redundantly propagating
                passedMsg["hash"+str(currentNodeClass)] = passedMsgNewMAC
            
                # If byzantine nodes have been caught up to this routing node, clear the history and optimize hops record
                passedMsg["trackHopClasses"] = passedMsg["trackHopClasses"][-1:]
                passedMsg["trackHops"] = passedMsg["trackHops"][-1:]

        else:
            # If the MAC between two nodes where correct put nodes in white list
            whiteNodeList = white_label_intermediate_nodes(passedMsg, currentNodeClass, previousNodeClass)
            if(len(whiteNodeList)>0):
                # ==== Message size optimization ====
                # Make sure there is no redundant healthy nodes are been reported
                # Check for healthy node indices, and if they are distinct report them
                calculatedWhiteNodes = white_label_intermediate_nodes(passedMsg, currentNodeClass, previousNodeClass)
                
                if memory_storage:
                    # Check if this discovery is an old existing one for the current node
                    # In case the discovery is old, discard adding it to the passedMsg
                    for healthyNode in calculatedWhiteNodes:
                        if healthyNode in graph.vs[currentNodeIndx]["found_white"]:
                            calculatedWhiteNodes.remove(healthyNode)
                        
                # Update in case the discovery was new
                for healthyNode in calculatedWhiteNodes:
                    if(healthyNode not in passedMsg["healthyNodes"]):
                        passedMsg["healthyNodes"].append( healthyNode )
                        # Check if this white node is already been labeled as byzantine in the current passed MAC_message
                        # And if so, clear it from byzantineNodeDict
                        if(healthyNode in passedMsg["byzantineNodeDict"]):
                            passedMsg["byzantineNodeDict"].remove(healthyNode)
                        
                        if memory_storage:
                            # Update current node memory with the discovery
                            graph.vs[currentNodeIndx]["found_white"].append(healthyNode)
        
        if(FC == True):
            passedMsg["trackHopClasses"] = passedMsg["trackHopClasses"][:-1]
            passedMsg["trackHops"] = passedMsg["trackHops"][:-1]
            
        # Return whether a byzantine node has been allegdly found or not ?
        if not report:
            return False
        else:
            return True
            

