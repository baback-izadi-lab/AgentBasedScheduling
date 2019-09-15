from osbrain import run_agent, run_nameserver, Agent
import time


class ManagerAgent(Agent):
    def on_init(self):
        self.bind('PUB', alias='MA')
        self.agent_count = self.get_attr('num_agents')

    def send_message(self, agent, msg):
        self.send(agent, msg)

    def get_message(self, message):
        self.agent_count -= 1
        self.log_info(self.name + ' : ' + str(message))
        if not self.agent_count:
            self.log_info('All tasks complete')


class TaskAgent(Agent):
    alpha = 0.5

    def get_message(self, message):
        self.agent_def = self.get_attr('agent_def')
        self.dag_data = self.get_attr('dag_data')
        self.current_proc = str(self.agent_def[self.name]['processor'] - 1)
        self.current_speed = self.agent_def[self.name]['speed']
        self.task_num = int(self.name[2:])
        self.exec_time = self.dag_data['proc_exec'][self.current_proc][self.current_speed][self.task_num]

        if isinstance(message, float):
            self.log_info('Available exec: {}'.format(
                float(message)+self.exec_time))
            self.avail_exec_time = float(message)+self.exec_time
        else:
            self.avail_exec_time = self.exec_time

        total_speeds = len(self.dag_data['proc_exec'][self.current_proc])
        new_speed = self.current_speed
        new_exec = self.exec_time
        for speed in range(total_speeds):
            if self.avail_exec_time > self.dag_data['proc_exec'][self.current_proc][speed][self.task_num]:
                new_exec = self.dag_data['proc_exec'][self.current_proc][
                    speed][self.task_num]
                new_speed = speed

        if new_speed != self.current_speed:
            self.log_info('Current exec time, speed: {}, {}. Setting NEW exec, speed: {},{}'.format(
                self.exec_time, self.current_speed, new_exec, new_speed))
            self.current_speed = new_speed
            self.exec_time = new_exec
        self.proc_power = self.dag_data['proc_power'][self.current_proc][self.current_speed][self.task_num]

        # Dummy execution time
        self.after(self.exec_time/4.0, self.send_complete)

    def send_complete(self, agent):
        actual_exec = round(self.exec_time*self.alpha, 3)
        slack_time = round(self.exec_time - actual_exec, 3)
        self.log_info('{} complete. Execution Time: {}. Slack Time: {}'.format(
            self.name, actual_exec, slack_time))
        self.log_info('Energy Consumed: {:.3f} Joules'.format(
            actual_exec*self.proc_power))
        self.send_message(self.name, slack_time)
        self.shutdown()

    def send_message(self, agent, msg):
        self.send(agent, msg)

    def on_init(self):
        self.bind('PUB', alias=self.name)
