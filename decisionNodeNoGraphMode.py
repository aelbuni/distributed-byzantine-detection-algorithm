import matplotlib.pyplot as plt
import csv     
    
def result_analysis(graph, whiteNodes, byzNodes, routedHopCount, numberMessages, NetworkMeshSize, nClasses):
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
    print "Positive Accuracy value (%) = " + str(accuracy)
    print "False Discovery Rate (%) = " + str(100-accuracy)
    print "False Detection = " + str(falseDetection)
    print "Number of sensors = " + str(NetworkMeshSize**2)
    print "Number of classes = " + str(nClasses)
    print "Total number of messages used = " + str(numberMessages)
    print "Total routed hop count = " + str(routedHopCount)
    
    # byzRealCount, trueDetection, falseDetection, trueDetectionAccuracy, accuracy, SensorCount, ClassesCount, routedHopCount, numberMessages
    with open('results.csv', 'a') as csvfile:
        resultwriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
        resultwriter.writerow([str(byzRealCount), str(trueDetection), str(falseDetection), str(100.0*trueDetection/(byzRealCount)), str(accuracy), str(NetworkMeshSize**2), str(nClasses), str(routedHopCount), str(numberMessages)])
    
    # Plot message complexity
    # plt.plot(messageSizeComplexity)
    # plt.title("Message Complexity")
    # plt.xlabel("Value")
    # plt.ylabel("Message Size")
    # plt.show()
