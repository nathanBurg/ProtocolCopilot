from src.dal.integrations.gemini_client import GeminiClientSingleton
from src.core.protocol_entities import Protocol, CreateProtocolRequest
from src.dal.database.protocol_dal import ProtocolDal

class ProtocolService:
    def __init__(self):
        self.gemini_client = GeminiClientSingleton().client
        self.protocol_dal = ProtocolDal()


    def create_protocol(request: CreateProtocolRequest) -> Protocol:
        