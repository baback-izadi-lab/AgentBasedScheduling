from osbrain import run_agent, run_nameserver, Agent
from agents import ManagerAgent, TaskAgent
import json
import time

if __name__ == '__main__':
    print("test")
    agent_def = json.load(open('agent_setup.json'))
    ns = run_nameserver()
    ma = run_agent('MA', base=ManagerAgent)

    agent_list = {}
    agent_list['MA'] = ma

    #Initializing task agents
    for agent_name in agent_def:
        agent_list[agent_name] = run_agent(agent_name, base=TaskAgent, attributes=agent_def[agent_name])
    
    #Setting up communication channels
    ta0 = agent_list['TA0']
    ta0.connect(ma.addr('MA'), handler='get_message')

    for agent_name in agent_def:
        agent_details = agent_def[agent_name]
        agent = agent_list[agent_name]
        for child_agent_name in agent_details['children']:
            child_agent = agent_list[child_agent_name]
            child_agent.connect(agent.addr(agent_name), handler='get_message')

    ma.send_message('MA', 'From MA: Start execution')

    while len(ns.agents()) > 1:
        time.sleep(1)
    ns.shutdown()