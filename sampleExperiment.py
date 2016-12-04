import numpy as np
import decisionNodeWithGraph as DN
import randomNetworkGenerator as GEN
import recursiveRandomRouting as DFD
import matplotlib.pyplot as plt
import utility as util

# =============== Initialize parameters ===========
sinkLocation = 0
meshSize = 10
numClasses = 3
numMessages = 900
numberHops = 10
numByzantine = np.floor((meshSize**2)/5) # 1/5 of the entire network size
mobility = False

g = GEN.generate_random_wanet_mesh_graph(meshSize, numClasses, numByzantine, 40, 12, sinkLocation)

# Save graph
# pkl_file = open('storedGraphs/myfile20.pkl', 'wb')
# g = pickle.dump(g, pkl_file)
# pkl_file.close()

# Load graph
# pkl_file = open('storedGraphs/myfile20.pkl', 'rb')
# g = pickle.load(pkl_file)
# pkl_file.close()

byzNodes, healthyNodes, byzListFormat, messageSizeComplexity, routedHopCount, energyConsum, energyConsumWithout = DFD.RecursiveRandomRouting(g, numClasses, meshSize, numberHops, sinkLocation)
        
for testCommunication in range(0, numMessages):
    if mobility:
        g = util.random_mobility(g, meshSize**2);
    byzNodes2, healthyNodes2, byzListFormat2, messageSizeComplexity2, routedHopCount2, energyConsum2, energyConsumWithout2 = DFD.RecursiveRandomRouting(g, numClasses, meshSize, numberHops, sinkLocation)
    # print "Message" + str(testCommunication) + " : " + str(g.vs[0]["msg"])
    byzNodes.extend(byzNodes2)
    healthyNodes.extend(healthyNodes2)
    byzListFormat.extend(byzListFormat2)
    routedHopCount += routedHopCount2
    messageSizeComplexity.extend(messageSizeComplexity2)
    energyConsum.extend(energyConsum2)
    energyConsumWithout.extend(energyConsumWithout2)

# no line highlights (false)
util.plot_save_graph(g, "graph.png", healthyNodes)
    
DN.result_analysis(g, healthyNodes, byzNodes, routedHopCount, messageSizeComplexity, meshSize, numClasses, energyConsum, energyConsumWithout)

# # plt.hist(byzNodes, bins = meshSize**2)
# # plt.title("byzNodes Histogram")
# # plt.xlabel("Value")
# # plt.ylabel("Frequency")
# # plt.show()