from .coolingCircuit import CoolingCircuit
from .utils.utils import *

from .coolingUnitary import checkInputMatrix
from .coolingUnitary import workCost

from qiskit import QuantumRegister
from qiskit import ClassicalRegister
from qiskit import QuantumCircuit

class HeatBathCooling():
    """
    ## HeatBathCooling(circuit,rounds,barriers)

    Class for the Heat Bath Cooling. 

    Parameters:
        coolingUnitary (numpy.ndarray or sparse._csr.csr_array): Cooling Unitary.
        rounds (int): number of rounds.
        OPTIONAL:
        barriers (bool): Barriers in the circuit.
    Return:
        HeatBathCooling (HeatBathCooling)
    Notes:
        The circuit cools the last qubit. 
    """
    _numQubits = None
    _coolingUnitary = None
    _barriers = False
    _rounds = 1
    _circuit = None
    _generatedCircuit = False
    def __init__(self,coolingUnitary=_coolingUnitary,rounds = _rounds,barriers=_barriers):
        self._numQubits,self._coolingUnitary = checkInputMatrix(coolingUnitary)
        self._rounds = rounds
        self._barriers = barriers
        if(self._rounds < 1 ):
            raise ValueError("Rounds have to be >= 1.")    
        self._circuit = self._buildCircuit(CoolingCircuit(self._numQubits,coolingUnitary=self._coolingUnitary,barriers=self._barriers),self._rounds)

    def getCircuit(self):
        """
        ## getCircuit()
        Return:
            Cooling Circuit (QuantumCircuit)
        """
        if(self._generatedCircuit == False):
            self._circuit = self._buildCircuit(CoolingCircuit(self._numQubits,coolingUnitary=self._coolingUnitary,barriers=self._barriers),self._rounds)
            self._generatedCircuit = True
        return self._circuit
    
    def calculateFinalProbability(self,excitedStateProbability):
        """
        ## calculateFinalProbability(excitedState)
            Calculate the final probability after the application of the circuit.

        Parameters:
            excitedStateProbability (float): Probability of the excited state.
        Return:
            Final State Probability (float)
        """ 
        numberOfStates = 2 ** self._numQubits
        if(not(isinstance(excitedStateProbability, list))):
            excitedStateProbability = self._numQubits * [excitedStateProbability]
        for j in range(self._rounds):
            initialVector = generateInitialVector(self._numQubits,excitedStateProbability)
            finalVector = initialVector.dot(self._coolingUnitary)
            finalprob = 1
            l = finalVector.tocoo().col
            for i in range(len(l)):
                if(l[i] < int(numberOfStates/2)):
                    finalprob -= finalVector[:, [l[i]]].data[0]
            excitedStateProbability[0] = finalprob
        if finalprob > 0:
            return finalprob
        else:
            return 0
    
    def calculateFinalTemperature(self,temperature,w):
        """
        ## calculateFinalProbability(excitedState)
            Calculate the final temperature after the application of the circuit.

        Parameters:
            temperature (float): temperature of the target qubit in milliKelvin (mK)
            w (float): Resonant frequency of qubit (GHz)
        Return:
            Final Temperature (float) : final temperature in milliKelvin (mK)
        """  
        prob = temperatureToProbability(temperature,w)
        return probabilityToTemperature(self.calculateFinalProbability(prob),w)
    
    def calculateWorkCost(self,excitedStateProbability,w=1):
        """
        ## calculateWorkCost(excitedStateProbability,w)
            Calculate the work cost of the Unitary.

        Parameters:
            excitedStateProbability (float): Probability of the excited state for all qubits.
            OR
            excitedStateProbability (list): Probability of the excited state for each qubit.
            (Optional) w (float): Resonant frequency of qubit (GHz)
        Return:
            Work Cost (float)
        """      
        workcost = 0
        numberOfStates = 2 ** self._numQubits
        if(not(isinstance(excitedStateProbability, list))):
            excitedStateProbability = self._numQubits * [excitedStateProbability]
        for j in range(self._rounds):
            #for each round calcolate the work cost
            workcost += workCost(self._coolingUnitary,excitedStateProbability,w) 
            initialVector = generateInitialVector(self._numQubits,excitedStateProbability)
            finalVector = initialVector.dot(self._coolingUnitary)
            finalprob = 1
            l = finalVector.tocoo().col
            for i in range(len(l)):
                if(l[i] < int(numberOfStates/2)):
                    finalprob -= finalVector[:, [l[i]]].data[0]
            #change the probability of the target qubit
            excitedStateProbability[0] = finalprob
        return workcost   
    
    def _buildCircuit(self,circuit,times):
        """
        Private: Build the circuit.
        """
        qubitsCircuit = circuit.num_qubits
        quantumRegisters = QuantumRegister(qubitsCircuit,"q")
        classicalRegisters = ClassicalRegister(1,"c")
        finalCircuit = QuantumCircuit(quantumRegisters,classicalRegisters)
        finalCircuit.compose(circuit, inplace=True)
        finalCircuit.reset(range(qubitsCircuit-1)) 
        for i in range(times-1):

            finalCircuit.compose(circuit, inplace=True)
            finalCircuit.reset(range(qubitsCircuit-1)) 
            
        return finalCircuit
    
    