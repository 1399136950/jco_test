import kNN  
from numpy import *   
  
dataSet, labels = kNN.createDataSet()  
  
testX = array([1.9, 3.2])  
k = 3  
outputLabel = kNN.kNNClassify(testX, dataSet, labels, 3)  
print ("Your input is:", testX, "and classified to class: ", outputLabel)  
  
testX = array([4.1, 3.3])  
outputLabel = kNN.kNNClassify(testX, dataSet, labels, 3)  
print ("Your input is:", testX, "and classified to class: ", outputLabel) 