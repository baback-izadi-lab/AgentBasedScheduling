from osbrain import run_agent, run_nameserver, Agent
import time

class ManagerAgent(Agent):
    def on_init(self):
        self.bind('PUB', alias='MA')
        self.agent_count = 5
    
    def send_message(self, agent, msg):
        self.send(agent, msg)

    def get_message(self, message):
        self.agent_count -= 1
        self.log_info(self.name + ' : ' + message)
        if not self.agent_count:
            self.log_info('All tasks complete')

class TaskAgent(Agent):
    def get_message(self, message):
        self.log_info(message)
        self.exec_time = self.get_attr('exec_time')
        #Dummy execution time
        self.after(self.exec_time/4.0, self.send_complete)
        
    def send_complete(self, agent):
        self.send_message(self.name, '{} complete. Execution Time: {}. Slack Time: {}'.format(self.name, self.exec_time, 0))
        self.shutdown()

    def send_message(self, agent, msg):
        self.send(agent, msg)

    def on_init(self):
        self.bind('PUB', alias=self.name)
