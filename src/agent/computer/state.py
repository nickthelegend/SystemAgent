from typing import TypedDict,Annotated
from src.message import BaseMessage
from operator import add

class AgentState(TypedDict):
    input:str
    messages:Annotated[list[BaseMessage],add]
    route:str
    agent_name:str
    agent_data:dict
    agent_request:str
    agent_response:str
    output:str