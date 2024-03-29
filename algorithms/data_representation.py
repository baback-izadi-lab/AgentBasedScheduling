import re
import json


class TGFFParser:
    def __init__(self):
        pass

    def parse(self, tgff_path, num_processors, speeds):
        self.num_processors = num_processors
        self.speeds = speeds
        self.tgff_path = tgff_path
        with open(self.tgff_path) as tgff:
            self.lines = tgff.read()
        self.get_arcs()
        self.get_tasks()
        self.final_data = {}
        self.final_data['arcs'] = self.arcs
        self.final_data['proc_exec'] = self.proc_exec
        self.final_data['proc_power'] = self.proc_power
        return self.final_data

    def write_json(self, output_file):
        json.dump(self.final_data, open(output_file, 'w'))

    def get_tasks(self):
        task_regex = re.compile(r'TASK\s\w+\sTYPE\s\d+')
        tasks = task_regex.findall(self.lines)
        self.process_tasks(tasks)

        # Parsing exec times
        self.proc_exec = {}
        for proc in range(self.num_processors):
            task_type_regex = re.compile(
                r'(?<=Proc' + re.escape(str(proc)) + r'Exec 0 {)(.[^}]*)(?=})', re.S)
            task_types = task_type_regex.findall(self.lines)
            prop = self.process_task_types(task_types[0], self.speeds[proc])
            exec_times = []
            for speed in range(self.speeds[proc]):
                exec_time_for_speed = []
                type_list_for_speed = prop[speed]
                for i, task_type in enumerate(self.tasks):
                    exec_time = type_list_for_speed[task_type]
                    exec_time_for_speed.append(exec_time)
                exec_times.append(exec_time_for_speed)

            self.proc_exec[proc] = exec_times

        # Parsing power
        self.proc_power = {}
        for proc in range(self.num_processors):
            task_type_regex = re.compile(
                r'(?<=Proc' + re.escape(str(proc)) + r'Power 0 {)(.[^}]*)(?=})', re.S)
            task_types = task_type_regex.findall(self.lines)
            prop = self.process_task_types(task_types[0], self.speeds[proc])
            exec_powers = []
            for speed in range(self.speeds[proc]):
                exec_power_for_speed = []
                type_list_for_speed = prop[speed]
                for i, task_type in enumerate(self.tasks):
                    exec_power = type_list_for_speed[task_type]
                    exec_power_for_speed.append(exec_power)
                exec_powers.append(exec_power_for_speed)

            self.proc_power[proc] = exec_powers

    def process_tasks(self, task_text):
        self.tasks = []
        for line in task_text:
            line = line.split()
            task = int(line[1].split('_')[1])
            task_type = int(line[3])
            self.tasks.append(task_type)

    def process_task_types(self, task_type_text, speeds):
        task_type_text = task_type_text.split()
        start = task_type_text.index('version')
        task_type_text = task_type_text[start+speeds+1:]
        task_property = []
        for i in range(speeds):
            prop = [float(a) for a in task_type_text[i+2:][::speeds+2]]
            task_property.append(prop)
        return task_property

    def get_arcs(self):
        arcs_type_regex = re.compile(r'(?<=time)(.[^}]*)(?=})', re.S)
        arcs_types = arcs_type_regex.findall(self.lines)
        self.process_arc_types(arcs_types[0])

        arcs_regex = re.compile(r'ARC.*', re.M)
        arcs = arcs_regex.findall(self.lines)
        self.process_arcs(arcs)

    def process_arc_types(self, arc_types_text):
        arc_types_text = arc_types_text.split()
        arc_numbers = arc_types_text[0:][::2]
        arc_numbers = [int(a) for a in arc_numbers]
        arc_values = arc_types_text[1:][::2]
        arc_values = [float(a) for a in arc_values]
        self.arc_types = dict(zip(arc_numbers, arc_values))

    def process_arcs(self, arcs_text):
        self.arcs = {}
        for line in arcs_text:
            line = line.split()
            arc = int(line[1].split('_')[1])
            from_task = int(line[3].split('_')[1])
            to_task = int(line[5].split('_')[1])
            arc_type = int(line[7])
            self.arcs[arc] = (from_task, to_task, self.arc_types[arc_type])


if __name__ == "__main__":
    parser = TGFFParser()
    data = parser.parse('../TaskGenerator/example_case0.tgff', 3, [1, 2, 3])
    parser.write_json('test.json')
