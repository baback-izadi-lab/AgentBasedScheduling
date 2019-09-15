from osbrain import run_agent, run_nameserver, Agent
from agents import ManagerAgent, TaskAgent
from ml_loop import Scheduler
# from algorithms import EDLS, data_representation
# from sklearn.bayes import GaussianNB
from comb_gen import CombGen
from TaskGenerator.SimulationData import TGFFGenerator, TGFFcommand
import json
import time


def data_reader(data):
    if isinstance(data, str):
        processed_data = json.load(open(data))
    else:
        processed_data = data
    return processed_data


def run_agents(schedule_path='agent_setup.json', dag_data='./algorithms/test.json'):
    agent_def = data_reader(schedule_path)
    dag_data = data_reader(dag_data)
    ns = run_nameserver()
    ma = run_agent('MA', base=ManagerAgent,
                   attributes=dict(num_agents=len(agent_def)))

    agent_list = {}
    agent_list['MA'] = ma

    # Initializing task agents
    for agent_name in agent_def:
        agent_list[agent_name] = run_agent(
            agent_name, base=TaskAgent, attributes={'dag_data': dag_data, 'agent_def': agent_def})

    # Setting up communication channels
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


if __name__ == '__main__':
    """
    print("Generating TGFF input file")
    tgff_gen = TGFFGenerator('dag_data.json', 'example_case1.tgffopt')
    tgff_gen.write_file()

    print("Running TGFF to generate dag")
    tc = TGFFcommand('example_case1')

    print("Parsing TGFF data")
    tgff_parser = data_representation.TGFFParser()
    dag = tgff_parser.parse('example_case1', 3, [1, 2, 3])

    print("Generating processor combinations")
    cg = CombGen(dag)
    processors = cg.proc_comb()

    scheduler = Scheduler(dag, processors, EDLS, GaussianNB)
    """
    run_agents()
