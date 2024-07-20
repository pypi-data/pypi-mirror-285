from dotenv import set_key
import os


conf = {
    #body data
    'publisher_hz' : 31,
    'num_muscles' : 131,
    'num_blendshapes' : 0,
    'num_priorities' : 1,
    'entry_byte_length' : 120,
    # server
    'frontend_port' : 5559,
    'backend_port' : 5556,
    'voice_frontend_port' : 5561,
    'voice_backend_port' : 5562,
    # client
    'ARTNet_IP' : 'localhost', 
    'tcpDataPubPort' : 5600,
    'tcpDataPubMonPort' : 5601,
    'tcpDataPubCtrlPort' : 5602,
    'tcpDataSubPort' : 5603,
    'tcpDataSubMonPort' : 5604,
    'tcpDataSubCtrlPort' : 5605,
    'tcpVoicePubPort' : 5606,
    'tcpVoicePubMonPort' : 5607,
    'tcpVoicePubCtrlPort' : 5608,
    'tcpVoiceSubPort' : 5609,
    'tcpVoiceSubMonPort' : 5610,
    'tcpVoiceSubCtrlPort' : 5611,
    'streamerHz' : 50,
    # client audio
    'chunkProportion' : 50,
    'audioLoopback' : False,
    # unreal client data
    'subscriberUDP_IP' : '127.0.0.1',
    'subscriberUDP_Port' : 7779,
    'streamerUDP_IP' : '',
    'streamerUDP_Port' : 1234,
}

class Config(object):
    def __init__(self):
        self._config = self._checkEnv(conf)
    
    # if an environmental variable for a particular config value is set, use it instead
    def _checkEnv(self, config:dict[str,any]):
        for key,val in config:
            config[key] = os.environ.get(key.upper(), default=val)
    
    def _get_property(self, property_name):
        if property_name not in self._config:
            return None
        return self._config[property_name]
    
    @classmethod
    def _get_property_list(cls) -> list[str]:
        return [x for x in dir(cls) if isinstance(getattr(cls,x),property)]
    
    def toFile(self,path:str='.env') -> list[tuple[bool | None, str, str]]:
        return [set_key(path,key,self._get_property(key)) for key in self._get_property_list()]
        
class ServerConfig(Config):
    pass

class ClientConfig(Config):
    pass

class UnrealClientConfig(Config):
    pass


