from src.agent.computer.utils import extract_agent_data,read_markdown_file
from src.message import AIMessage,HumanMessage,SystemMessage
from langgraph.graph import StateGraph,START,END
from src.agent.web import WebAgent,BrowserConfig
from src.agent.computer.state import AgentState
from src.agent.terminal import TerminalAgent
from src.agent.system import SystemAgent
from src.inference import BaseInference
from src.agent import BaseAgent
from termcolor import colored
from datetime import datetime
from getpass import getuser
from pathlib import Path
import platform

class ComputerAgent(BaseAgent):
    def __init__(self, llm:BaseInference=None, use_vision:bool=False, max_iteration:int=10, 
                 token_usage:bool=False, verbose:bool=False, use_tts:bool=False, tts=None):
        self.name='Computer Agent'
        self.description='This agent tries to simulate a human using the computer'
        self.system_prompt=read_markdown_file('src/agent/computer/prompt/system.md')
        self.human_prompt=read_markdown_file('src/agent/computer/prompt/human.md')
        self.max_iteration=max_iteration
        self.iteration=0
        self.llm=llm
        self.verbose=verbose
        self.token_usage=token_usage
        self.use_vision=use_vision
        self.use_tts = use_tts
        self.tts = tts
        self.graph=self.create_graph()

    def reason(self,state:AgentState):    
        message=self.llm.invoke(state.get('messages'))
        agent_data=extract_agent_data(message.content)
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        agent_name=agent_data.get('Agent Name')
        agent_request=agent_data.get('Request')
        
        if self.verbose:
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
            
        # Speak the thought process
        if self.use_tts and self.tts and thought:
            self.tts.speak(f"Thinking: {thought}")
            
        return {**state,'agent_data': agent_data,'messages':[message],'route':route,'agent_name':agent_name,'agent_request':agent_request}
    
    def web(self,state:AgentState):
        agent_name = "Web Agent"
        agent_request = state.get("agent_request")
        
        if self.verbose:
            print(colored(f'Agent Name: {agent_name}',color='yellow',attrs=['bold']))
            print(colored(f'Agent Request: {agent_request}',color='green',attrs=['bold']))
            
        # Speak the agent request
        if self.use_tts and self.tts:
            self.tts.speak(f"Using {agent_name} to {agent_request}")
            
        config=BrowserConfig(browser='edge',headless=False)
        agent=WebAgent(config=config,llm=self.llm,max_iteration=self.max_iteration,verbose=self.verbose,use_vision=self.use_vision,token_usage=self.token_usage)
        agent_response=agent.invoke(agent_request)
        human_prompt=self.human_prompt.format(agent=agent_name,response=agent_response)
        message=HumanMessage(human_prompt)
        
        if self.verbose:
            print(colored(f'Agent Response: {agent_response}',color='blue',attrs=['bold']))
            
        # Speak a summary of the response
        if self.use_tts and self.tts:
            # Create a shorter summary for speech
            summary = f"{agent_name} completed the task."
            if len(agent_response) > 200:
                summary += " The response is quite detailed."
            else:
                summary += f" Response: {agent_response[:100]}"
                
            self.tts.speak(summary)
            
        return {**state,'messages':[message],'agent_response':agent_response}

    def terminal(self,state:AgentState):
        agent_name = "Terminal Agent"
        agent_request = state.get("agent_request")
        
        if self.verbose:
            print(colored(f'Agent Name: {agent_name}',color='yellow',attrs=['bold']))
            print(colored(f'Agent Request: {agent_request}',color='green',attrs=['bold']))
            
        # Speak the agent request
        if self.use_tts and self.tts:
            self.tts.speak(f"Using {agent_name} to {agent_request}")
            
        agent=TerminalAgent(llm=self.llm,max_iteration=self.max_iteration,verbose=self.verbose,token_usage=self.token_usage)
        agent_response=agent.invoke(agent_request)
        human_prompt=self.human_prompt.format(agent=agent_name,response=agent_response)
        message=HumanMessage(human_prompt)
        
        if self.verbose:
            print(colored(f'Agent Response: {agent_response}',color='blue',attrs=['bold']))
            
        # Speak a summary of the response
        if self.use_tts and self.tts:
            # Create a shorter summary for speech
            summary = f"{agent_name} completed the task."
            if len(agent_response) > 200:
                summary += " The response is quite detailed."
            else:
                summary += f" Response: {agent_response[:100]}"
                
            self.tts.speak(summary)
            
        return {**state,'messages':[message],'agent_response':agent_response}

    def system(self,state:AgentState):
        agent_name = "System Agent"
        agent_request = state.get("agent_request")
        
        if self.verbose:
            print(colored(f'Agent Name: {agent_name}',color='yellow',attrs=['bold']))
            print(colored(f'Agent Request: {agent_request}',color='green',attrs=['bold']))

        # Speak the agent request
        if self.use_tts and self.tts:
            self.tts.speak(f"Using {agent_name} to {agent_request}")
            
        agent=SystemAgent(llm=self.llm,max_iteration=self.max_iteration,verbose=self.verbose,use_vision=self.use_vision,token_usage=self.token_usage)
        agent_response=agent.invoke(agent_request)
        human_prompt=self.human_prompt.format(agent=agent_name,response=agent_response)
        message=HumanMessage(human_prompt)
        
        if self.verbose:
            print(colored(f'Agent Response: {agent_response}',color='blue',attrs=['bold']))
            
        # Speak a summary of the response
        if self.use_tts and self.tts:
            # Create a shorter summary for speech
            summary = f"{agent_name} completed the task."
            if len(agent_response) > 200:
                summary += " The response is quite detailed."
            else:
                summary += f" Response: {agent_response[:100]}"
                
            self.tts.speak(summary)
            
        return {**state,'messages':[message],'agent_response':agent_response}

    def final(self,state:AgentState):
        agent_data=state.get('agent_data')
        final_answer=agent_data.get('Final Answer')
        
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='blue',attrs=['bold']))
        
        # Speak the final answer
        if self.use_tts and self.tts:
            self.tts.speak(f"Final answer: {final_answer}")
            
        return {**state,'output':final_answer}

    def controller(self,state:AgentState):
        if self.iteration<self.max_iteration:
            self.iteration+=1
            route = state.get('route').lower()
            
            # Speak the routing decision
            if self.use_tts and self.tts:
                if route == 'agent':
                    agent_name = state.get('agent_name')
                    self.tts.speak(f"Routing to {agent_name}")
                elif route == 'final':
                    self.tts.speak("Preparing final answer")
            
            if route == 'agent':
                agent_name = state.get('agent_name')
                return agent_name.lower()
            else:
                return 'final'
        else:
            if self.use_tts and self.tts:
                self.tts.speak("Maximum iterations reached. Preparing final answer.")
            return 'final'

    def create_graph(self):
        workflow=StateGraph(AgentState)
        workflow.add_node('reason',self.reason)
        workflow.add_node('web',self.web)
        workflow.add_node('terminal',self.terminal)
        workflow.add_node('system',self.system)
        workflow.add_node('final',self.final)

        workflow.add_edge(START,'reason')
        workflow.add_conditional_edges('reason',self.controller)
        workflow.add_edge('web','reason')
        workflow.add_edge('terminal','reason')
        workflow.add_edge('system','reason')
        workflow.add_edge('final',END)

        return workflow.compile(debug=False)

    def invoke(self,input:str):
       if self.verbose:
            print(f'Entering '+colored(self.name,'black','on_white'))
            
       # Speak the task
       if self.use_tts and self.tts:
            self.tts.speak(f"Starting new task: {input}")
            
       parameters={
           'username': getuser(),
           'os': platform.platform(),
           'pc_name': platform.node(),
           'home_dir': Path.home().as_posix(),
           'datetime': datetime.now().strftime('%Y-%m-%d'),
       }
       state={
           'input':input,
           'agent_data':{},
           'messages':[SystemMessage(self.system_prompt.format(**parameters)),HumanMessage(f'Task: {input}')],
           'output':'',
           'route':'',
           'agent_name':'',
           'agent_request':'',
           'agent_response':''
       }
       agent_response=self.graph.invoke(state)
       return agent_response.get('output')

    def stream(self,input:str):
        pass

