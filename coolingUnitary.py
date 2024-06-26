from collections import Counter
import numpy as np
from scipy.sparse import csr_array
from utils import *

class CoolingUnitary:
    """
    ## CoolingUnitary(numQubits,swapList)
    Class for a CoolingUnitary.

    Parameters:
        numQubits (int): Number of qubits.
        swapList (list): List to describe the states to be swapped.
    Return:
        coolingUnitary (numpy.ndarray)

    EXAMPLES:

    - Single Swap: `[["000","001"]] 000 <---> 001`
    - Single Swap with integer: `[[0,1]] 000 (0) <---> 001 (1)`
    - Cycle of length 3: `[["000","001","010"]] 000 --> 001 --> 010 --> 000`
    - 2 Cycles of length 2: `[["000","001"], ["010","011"]] 000 <---> 001 , 010 <---> 011`
    
    """
    
    _swapList = [["000","001"]]
    _numQubits = 3
    coolingUnitary = None

    def __new__(cls,numQubits=_numQubits,swapList=_swapList):
        cls._checkInputParameters(cls,numQubits,swapList)
        cls._numQubits = numQubits
        cls._swapList = swapList
        cls._swapList = listIntegerToBinary(cls._swapList,numQubits)
        cls._makeMatrix(cls)
        return cls.coolingUnitary
    
    def _checkInputParameters(self,numQubits,swapList):
        """
        Private: Check of the Input parameters.
        """   
        outputMessage = "The Input Parameters are not well formatted"
        maxPossibleValue = (2 ** numQubits)
        greaterInteger = -1
        listToCount = []
        if(len(swapList) == 0):
            raise ValueError("List is empty")
        for index in range(len(swapList)):
            for i in range(len(swapList[index])):
                #Saving the greater Integer found in the list
                if(greaterInteger < binaryToInteger(swapList[index][i])):
                    greaterInteger = binaryToInteger(swapList[index][i])
                if(binaryToInteger(swapList[index][i]) < 0):
                    ValueError("Negative integer")
                listToCount.append(binaryToInteger(swapList[index][i]))
        #If the variable is -1 then it is not a string or an integer.
        #If a value is greater than 2 ^ N then error
        if(greaterInteger == -1 or greaterInteger > maxPossibleValue-1):
            raise ValueError(outputMessage)
        
        #Check if a state is repeated two times
        counts = Counter(listToCount)
        for element,count in counts.items():
            if(count > 1):
                raise ValueError("A swap state is used more than 1 time")
       
    def _makeMatrix(self):
        """
        Private: Creation of the Unitary. 
        """ 
        numOfStates = 2**self._numQubits
        #self.coolingUnitary = np.eye((numOfStates))
        row = []
        col = []
        data = [1]*numOfStates
        v = [-1] * numOfStates
        for index in range(len(self._swapList)):
            for i in range(len(self._swapList[index])-1):
                
                element = binaryToInteger(self._swapList[index][i])
                succElement = binaryToInteger(self._swapList[index][i+1])

                #Insert in the vector the element we want to swap to
                v[element] = succElement

            #Same thing as above but last state in the cycle is matched with the first one
            element = binaryToInteger(self._swapList[index][len(self._swapList[index])-1])
            firstElement = binaryToInteger(self._swapList[index][0])
            
            v[element] = firstElement

        #Using the created vector we can create the matrix
        #If v[i] == -1 the state is matched with itself, otherwise we use the vector
        #To determinate the state to swap to
        for i in range(numOfStates):
            if(v[i] == -1):
                row.append(i) 
                col.append(i) 
            else:
                row.append(v[i])
                col.append(i)
        
        self.coolingUnitary = csr_array((data, (row, col)), shape=(numOfStates, numOfStates))



