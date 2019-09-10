import os
import json


class TGFFGenerator:
    """This class generates the TGFF file it needs path to TGFF in the config file"""

    def __init__(self, json_data_path, tgff_filename, tgff_path="./"):
        """Pass TaskGraphData and filename ONLY of the tgff file"""
        self.data = json.load(open(json_data_path))
        self.tgff_path = tgff_path
        self.tgff_path_example = self.tgff_path
        self.tgff_filename = tgff_filename + '.tgffopt'
        self.write_file()

    def write_file(self):
        """Writes the tgffopt file to the examples directory of the tgff folder"""
        # print "I'm in TGFFGenerator write_file!"
        self.tgff_file = open(self.tgff_path_example+self.tgff_filename, 'w+')
        lines = []
        lines.append('tg_cnt 1\n')
        lines.append('task_cnt {} 1\n'.format(2*self.data['num_tasks']))
        lines.append('task_degree {} {}\n'.format(
            self.data['indegree'], self.data['outdegree']))
        lines.append('task_type_cnt {}\n'.format(self.data['num_tasks']))
        lines.append('trans_type_cnt {}\n'.format(self.data['num_tasks']*2))
        lines.append(
            "\nperiod_laxity 1 \nperiod_mul 1,0.5,2 \ntg_write \neps_write \nvcg_write")
        # writing the details of processors into tgff file
        for proc in range(self.data['num_proc']):
            lines.append(
                '\ntable_label Proc{}Exec\ntable_cnt 1\ntype_attrib'.format(proc))
            for speed in range(self.data['num_speeds'][proc]):
                if speed == 0:
                    lines.append(' ')
                else:
                    lines.append(',')
                key = '{}_{}'.format(proc, speed)
                proc_details = self.data['proc_details'][proc]
                average_exec = str(proc_details['exec_average'][speed])
                variation_exec = str(proc_details['exec_variation'][speed])
                lines.append(' exec{} {} {} 0.1'.format(
                    key, average_exec, variation_exec))
            lines.append('\npe_write\n')
            lines.append('\ntable_label Proc{}Power'.format(proc))
            lines.append('\ntable_cnt 1')
            lines.append('\ntype_attrib ')
            for speed in range(self.data['num_speeds'][proc]):
                if speed == 0:
                    lines.append(' ')
                else:
                    lines.append(',')
                key = '{}_{}'.format(proc, speed)
                proc_details = self.data['proc_details'][proc]
                average_power = str(proc_details['power_average'][speed])
                variation_power = str(proc_details['power_variation'][speed])
                lines.append(' power{} {} {} 0.1'.format(
                    key, average_power, variation_power))
            lines.append('\npe_write\n')
        lines.append('\ntable_label arcs \ntable_cnt 1 \ntype_attrib time {} {} \ntrans_write'.format(
            self.data['arc_average'], self.data['arc_variation']))
        self.tgff_file.writelines(lines)
        self.tgff_file.close()


class TGFFcommand:
    """Runs the TGFF command"""

    def __init__(self, tgff_filename):
        self.tgff_filename = tgff_filename
        self.tgff_path = "/home/kabir/Downloads/tgff-3.6/"
        self.tgff_path_example = self.tgff_path + 'examples/'
        self.tgff_filename = tgff_filename + '.tgffopt'
        #retcode = subprocess.call([self.tgff_path+'tgff',self.tgff_path_example+tgff_filename])
        retcode = os.system(self.tgff_path+'tgff ' +
                            self.tgff_path_example+tgff_filename)
        # print retcode


class Processor:
    "stores execution times and power consumed by the processor for each task"

    def __init__(self, speeds, tasks):
        self.speeds = speeds
        self.tasks = tasks
        self.exec_time = [[0 for count in range(
            tasks)] for count in range(speeds)]
        self.power = [[0 for count in range(tasks)] for count in range(speeds)]
        self.initial_temperature = [[0 for count in range(tasks)] for count in
                                    range(speeds)]  # array of initial temperature values during iterations
        self.final_temperature = [[0 for count in range(tasks)] for count in
                                  range(speeds)]  # array of final temperature values during iterations
        self.DA = [0] * tasks
        self.Dyn = [0] * tasks
        self.DL = [0] * tasks
        self.TF = [0] * tasks
        self.delta = [0] * tasks
        self.alpha = [0] * tasks
        self.temp = [0] * tasks  # can be changed to norm_temp later
        self.queue = []
        self.currentTime = 0

    def add_exec(self, execTime, speed, task):
        self.exec_time[speed][task] = execTime

    # print "Printing execution time"
    # print self.exec_time

    def add_power(self, power, speed, task):
        self.power[speed][task] = power


class Edge:
    "stores info about edge"

    def __init__(self, source, dest, value):
        self.source = source
        self.dest = dest
        self.value = value
        # def disp(self):
        #print("Source =  %i  Dest =  %i  Value =  %d" )%(self.source,self.dest,self.value)


class TGFFParser:
    """This class is the final step in creation of the digraph
    It reads the TGFF file generated and stores the data into the TaskGraph class"""

    def __init__(self, data, tgff_filename, g):
        # print "I'm in TGFFParser __int__!"
        self.g = g
        self.data = data
        # self.tgff_filename = tgff_filename
        #cm = ConfigModifier()
        #self.tgff_path = cm.get_value('tgff_path')
        self.tgff_path = 'C:/Users/shekar/Desktop/All Projects/New Paltz/tgff/tgff-3.6/'
        self.tgff_path_example = self.tgff_path + 'examples/'
        self.tgff_filename_opt = tgff_filename + '.tgffopt'
        self.tgff_filename = tgff_filename + '.tgff'
        for proc in range(data.num_proc):
            p = Processor(data.get_num_speeds(proc), data.get_num_tasks())
            g.processors.append(p)

    def parse_tgff(self):
        """Reads the tgff file"""
        # print "I'm in TGFFParser parse_tgff!"
        self.tgff_file = open(self.tgff_path_example+self.tgff_filename, 'r')
        text = self.tgff_file.readlines()
        lc = 0
        for line in text:
            words = line.split()
        for word in words:
            if(word == 'ARC'):
                e = Edge(int(words[3].split("")[1]),
                         int(words[5].split("")[1]), 1)
                self.g.set_edge(e)
            if(word == '@arcs'):
                # print "Creating arcs!!!"
                for x in range(self.g.num_edges):
                    # print text[lc+x+6].split()[0] # OR HERE?
                    # print float(text[lc+x+6].split()[1]) #problem starts from here!
                    self.g.weight[self.g.edge_list[x].source][self.g.edge_list[x].dest] = float(
                        text[lc+x+6].split()[1])  # OR IS IT HERE?
                    self.g.edge_list[x].value = float(text[lc+x+6].split()[1])
        for proc in range(self.data.num_proc):
            if(word == 'exec' + str(proc) + str(self.data.get_num_speeds(proc)-1)):
                task = 0
                for entry in range(lc+1, (lc+(self.data.num_tasks)+1)):
                    for speed in range(self.data.get_num_speeds(proc)):
                        self.g.processors[proc].add_exec(
                            float(text[entry].split()[2+speed]), speed, task)
                        task += 1
            if(word == 'power' + str(proc) + str(self.data.get_num_speeds(proc)-1)):
                task = 0
                for entry in range(lc+1, lc+self.data.num_tasks+1):
                    for speed in range(self.data.get_num_speeds(proc)):
                        self.g.processors[proc].add_power(
                            float(text[entry].split()[2+speed]), speed, task)
                        task += 1
            lc += 1
        return self.g


if __name__ == "__main__":
    print("This is Start of main")
    data_file_path = 'dag_data.json'
    tg = TGFFGenerator(data_file_path, 'example_case1')
    tg.write_file()
    #tc =TGFFcommand('example_case0')
