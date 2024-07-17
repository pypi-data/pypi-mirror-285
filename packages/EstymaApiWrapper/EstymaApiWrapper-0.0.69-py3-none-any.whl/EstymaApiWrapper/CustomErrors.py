class SettingNotAvailableException(Exception):
    pass
    #print("The setting does not exist")

class SettingAlreadyHasTargetValue(Exception):
    pass
    #print("Setting already has target value")

class ClientNotInitialized(Exception):
    pass
    #print("Estyma API Client is not initialized")
    #print("Initialize the client before using it")