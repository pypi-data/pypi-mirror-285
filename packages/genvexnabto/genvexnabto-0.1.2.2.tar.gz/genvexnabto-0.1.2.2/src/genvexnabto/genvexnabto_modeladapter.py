from typing import Dict, List
from collections.abc import Callable
from .models import ( GenvexNabtoBaseModel, GenvexNabtoOptima270, GenvexNabtoOptima260, GenvexNabtoOptima251, GenvexNabtoOptima250, 
                     GenvexNabtoCTS400,
                     GenvexNabtoDatapoint, GenvexNabtoDatapointKey, GenvexNabtoSetpoint, GenvexNabtoSetpointKey )

class GenvexNabtoModelAdapter:
    _loadedModel: GenvexNabtoBaseModel = None

    _currentDatapointList: Dict[int, List[GenvexNabtoDatapointKey]] = {}
    _currentSetpointList: Dict[int, List[GenvexNabtoSetpointKey]] = {}

    _values = {}
    _update_handlers: Dict[GenvexNabtoDatapointKey|GenvexNabtoSetpointKey, List[Callable[[int, int], None]]] = {}

    def __init__(self, model, deviceNumber, slaveDeviceNumber, slaveDeviceModel):
        if model == 2010 and deviceNumber == 79265:
            self._loadedModel = GenvexNabtoOptima270()
        elif model == 1040 and slaveDeviceNumber == 70810 and slaveDeviceModel == 26:
            self._loadedModel = GenvexNabtoOptima260()
        elif model == 1040 and slaveDeviceNumber == 79250 and slaveDeviceModel == 8:
            self._loadedModel = GenvexNabtoOptima251()
        elif model == 1040 and slaveDeviceNumber == 79250 and slaveDeviceModel == 1:
            self._loadedModel = GenvexNabtoOptima250()
        elif (model == 1141 or model == 1140) and slaveDeviceNumber == 72270:
            self._loadedModel = GenvexNabtoCTS400()
        else:
            self._loadedModel = GenvexNabtoBaseModel()
            
        self._currentDatapointList = {100: self._loadedModel.getDefaultDatapointRequest()}
        self._currentSetpointList = {200: self._loadedModel.getDefaultSetpointRequest()}

    def getModelName(self):
        return self._loadedModel.getModelName()
    
    def getManufacturer(self):
        return self._loadedModel.getManufacturer()

    @staticmethod
    def providesModel(model, deviceNumber, slaveDeviceNumber, slaveDeviceModel):
        if model == 2010 and deviceNumber == 79265:
            return True
        if model == 1040 and (slaveDeviceNumber == 70810 or slaveDeviceNumber == 79250):
            if slaveDeviceModel == 26 or slaveDeviceModel == 1 or slaveDeviceModel == 8:
                return True
        if model == 1141 or model == 1140: #Nilan
            if slaveDeviceNumber == 72270: #72270  = CTS400 | 2763306 = CTS602 - Not even sure values are correct, so disabled for now!
                return True
        return False
    
    def providesValue(self, key: GenvexNabtoSetpointKey|GenvexNabtoDatapointKey):
        if self._loadedModel.modelProvidesDatapoint(key) or self._loadedModel.modelProvidesSetpoint(key):
            return True 
        return False

    def hasValue(self, key: GenvexNabtoSetpointKey|GenvexNabtoDatapointKey) -> bool:
        return key in self._values
    
    def getValue(self, key: GenvexNabtoSetpointKey|GenvexNabtoDatapointKey):
        return self._values[key]
    
    def getMinValue(self, key: GenvexNabtoSetpointKey):
        if self._loadedModel.modelProvidesSetpoint(key): 
            return (self._loadedModel._setpoints[key]['min'] + self._loadedModel._setpoints[key]['offset']) / self._loadedModel._setpoints[key]['divider']
        return False
    
    def getMaxValue(self, key: GenvexNabtoSetpointKey):
        if self._loadedModel.modelProvidesSetpoint(key): 
            return (self._loadedModel._setpoints[key]['max'] + self._loadedModel._setpoints[key]['offset']) / self._loadedModel._setpoints[key]['divider']
        return False
    
    def getSetpointStep(self, key: GenvexNabtoSetpointKey):
        if self._loadedModel.modelProvidesSetpoint(key):             
            return self._loadedModel._setpoints[key]['step']
        return False
    
    def registerUpdateHandler(self, key: GenvexNabtoSetpointKey|GenvexNabtoDatapointKey, updateMethod: Callable[[int, int], None]):
        if key not in self._update_handlers:
            self._update_handlers[key] = []
        self._update_handlers[key].append(updateMethod)

    def notifyAllUpdateHandlers(self):
        for key in self._update_handlers:
            for method in self._update_handlers[key]:
                method(-1, self._values[key])

    
    def getDatapointRequestList(self, sequenceId):
        if sequenceId not in self._currentDatapointList:
            return False
        returnList = []
        for key in self._currentDatapointList[sequenceId]:
            returnList.append(self._loadedModel._datapoints[key])
        return returnList
    
    def getSetpointRequestList(self, sequenceId):
        if sequenceId not in self._currentSetpointList:
            return False
        returnList = []
        for key in self._currentSetpointList[sequenceId]:
            returnList.append(self._loadedModel._setpoints[key])
        return returnList
    
    def parseDataResponce(self, responceSeq, responcePayload):
        print(f"Got dataresponce with sequence id: {responceSeq}")
        if responceSeq in self._currentDatapointList:
            print(f"Is a datapoint responce")
            return self.parseDatapointResponce(responceSeq, responcePayload)
        if responceSeq in self._currentSetpointList:
            print(f"Is a setpoint responce")
            return self.parseSetpointResponce(responceSeq, responcePayload)

    def parseDatapointResponce(self, responceSeq, responcePayload):
        if responceSeq not in self._currentDatapointList:
            return False
        decodingKeys = self._currentDatapointList[responceSeq]
        print(decodingKeys)
        responceLength = int.from_bytes(responcePayload[0:2])
        for position in range(responceLength):
            valueKey = decodingKeys[position]
            payloadSlice = responcePayload[2+position*2:4+position*2]
            oldValue = -1
            if valueKey in self._values:
                oldValue = self._values[valueKey]
            self._values[valueKey] = (int.from_bytes(payloadSlice, 'big') + self._loadedModel._datapoints[valueKey]['offset']) / self._loadedModel._datapoints[valueKey]['divider']
            if oldValue != self._values[valueKey]:
                if valueKey in self._update_handlers:
                    for method in self._update_handlers[valueKey]:
                        method(oldValue, self._values[valueKey])
        return
    
    def parseSetpointResponce(self, responceSeq, responcePayload):
        if responceSeq not in self._currentSetpointList:
            return False
        decodingKeys = self._currentSetpointList[responceSeq]
        responceLength = int.from_bytes(responcePayload[1:3])
        for position in range(responceLength):
            valueKey = decodingKeys[position]
            payloadSlice = responcePayload[3+position*2:5+position*2]
            oldValue = -1
            if valueKey in self._values:
                oldValue = self._values[valueKey]
            self._values[valueKey] = (int.from_bytes(payloadSlice, 'big') + self._loadedModel._setpoints[valueKey]['offset']) / self._loadedModel._setpoints[valueKey]['divider']
            if oldValue != self._values[valueKey]:
                if valueKey in self._update_handlers:
                    for method in self._update_handlers[valueKey]:
                        method(oldValue, self._values[valueKey])
        return

