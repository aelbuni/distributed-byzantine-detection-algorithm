import matplotlib.pyplot as plt
import csv     
    
def result_analysis(graph, whiteNodes, byzNodes, routedHopCount, messageSizeComplexity, NetworkMeshSize, nClasses, energyConsum, energyConsumWithout):
    falseDetection = 0
    trueDetection = 0
    
    # Select distinct nodes labeled as faulty
    byzNodes = set(byzNodes)
    
    # Remove white labeled nodes from the faulty set
    finalDecision = byzNodes.difference(whiteNodes)
    
    # Count total byzNodes
    byzRealCount = len(graph.vs(color_eq="black"))
    
    for node in finalDecision:
        if(graph.vs[node]["color"]=="black"):
            trueDetection+=1
        else:
            falseDetection+=1
    
    # Calculat PPV (Positive Accuracy value)
    total = trueDetection + falseDetection
    if total!=0:
        accuracy = 100.0*trueDetection/(total)
    else:
        accuracy = 0
        
    print "Real faulty count = " + str(byzRealCount)
    print "True/False Detection Ratio = " + str(trueDetection) + " / " + str(falseDetection)
    print "Correct Detection Accuracy (%) = " + str(100.0*trueDetection/(byzRealCount))
    print "Accuracy (%) = " + str(accuracy)
    print "False Discovery Rate (%) = " + str(100-accuracy)
    print "False Detection = " + str(falseDetection)
    print "Number of sensors = " + str(NetworkMeshSize**2)
    print "Number of classes = " + str(nClasses)
    print "Total routed hop count = " + str(routedHopCount)
    
    # byzRealCount, trueDetection, falseDetection, trueDetectionAccuracy, accuracy, falseDetection, SensorCount, ClassesCount, routedHopCount
    with open('results.csv', 'a') as csvfile:
        resultwriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        resultwriter.writerow([str(byzRealCount), str(trueDetection), str(falseDetection), str(100.0*trueDetection/(byzRealCount)), str(accuracy), str(falseDetection), str(NetworkMeshSize**2), str(nClasses), str(routedHopCount)])
    
    totalEnergy = 0.0
    totalOriginalEnergy = 0.0
    for i in range(0, NetworkMeshSize**2):
        totalEnergy += graph.vs[i]["energy"]
        totalOriginalEnergy += graph.vs[i]["original_energy"]
    
    print "Total Energy Consumed With DFD Algorithm = " + str(totalEnergy) + " J"    
    print "Total Energy Consumed Without DFD Algorithm = " + str(totalOriginalEnergy) + " J"
    print "Energy Overhead Ratio = " + str(totalEnergy*1.0/totalOriginalEnergy) 
    
    with open('results-energy.csv', 'w') as csvfile:
        resultwriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        resultwriter.writerow(['energy', 'energyWith'])
        for record in range(1, len(energyConsum)):
                resultwriter.writerow([str(energyConsum[record]), energyConsumWithout[record]])
    
    #Plot message complexity
    # plt.plot(messageSizeComplexity)
    # plt.title("Message Complexity")
    # plt.xlabel("Value")
    # plt.ylabel("Message Size (Bytes)")
    # plt.show()

    # a = energyConsum
    # b = energyConsumWithout
    # # a[:] = [2-x for x in a]
    # # b[:] = [2-x for x in b]
    
    # plt.plot(a,'r') # plotting t,a separately 
    # plt.plot(b,'b') # plotting t,b separately
    # plt.title("Energy consumption comparison")
    # plt.xlabel("Time")
    # plt.ylabel("Joule")
    # plt.show()