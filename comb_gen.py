import copy
import os


class Task:
    """This class represents the information stored in each node"""

    def __init__(self, number):
        self.number = number
        self.SL = 0


class Edge:
    "stores info about edge"

    def __init__(self, source, dest, value):
        self.source = source
        self.dest = dest
        self.value = value
        # def disp(self):
        #print("Source =  %i  Dest =  %i  Value =  %d" )%(self.source,self.dest,self.value)


class Digraph:
    """uses node, edge and processor classes in this class to create digraphs"""

    def __init__(self, tasks, procs):
        self.total_energy = 0
        self.total_exec_time = 0
        self.num_tasks = tasks
        self.num_processors = procs
        self.links = [[0 for count in range(tasks)] for count in range(tasks)]
        self.parent = [None for count in range(tasks)]
        self.weight = [[0 for count in range(tasks)] for count in range(tasks)]
        self.tasks = []  # array of tasks
        self.scheduled_tasks = []  # array of scheduled tasks
        self.processors = []  # array of processors
        self.task_queue = []  # queue of tasks
        self.num_edges = 0
        self.edge_list = []  # list of edges
        # array of temperature values
        self.temperature = [313.15 for count in range(procs)]
        self.temperature_values = []
        self.task_order = []
        self.current_task = 0
        self.current_time = 0.0
        self.ro = 0.0
        self.beta = 0.0
        # print "temperature = %s" %(self.temperature)
        for i in range(self.num_tasks):
            t = Task(i)
            self.tasks.append(t)

    def nodes(self):  # returns number of tasks
        return self.num_tasks

    def out_degree(self, task):  # returns number of tasks going out
        total = 0
        for count in range(self.num_tasks):
            if (self.links[task][count]):
                total += 1
        return total

    def in_degree(self, task):  # returns number of tasks coming in
        total = 0
        for count in range(self.num_tasks):
            if (self.links[count][task]):
                total += 1
        return total

    def has_prev_link(self, task):  # checks if node has prev nodes
        val = 0
        for count in range(self.num_tasks):
            if (self.links[count][task]):
                val = 1
        return val

    def has_next_link(self, task):
        val = 0
        for count in range(self.num_tasks):
            if (self.links[task][count]):
                val = 1
        return val

    def has_link(self, task1, task2):
        if (self.links[task1][task2]):
            return 1
        else:
            return 0

    def next_task(self, task):
        if (self.has_next_link(task)):
            # print "Task %i has link!" %(task)
            next = []
            for count in range(self.num_tasks):
                if (self.has_link(task, count)):
                    next.append(count)
            return next

    def prev_node(self, task):
        # print "has prev link value = " + str(self.has_prev_link(task))
        if (self.has_prev_link(task)):
            prev = []
            for count in range(self.num_tasks):
                #	print str(count) + " and " + str(task) + " has a link"
                if (self.has_link(count, task)):
                    prev.append(count)
            return prev

    def set_edge(self, edge):
        if (self.links[edge.source][edge.dest] == 0):
            self.parent[edge.dest] = edge.source
            self.links[edge.source][edge.dest] = 1
            self.weight[edge.source][edge.dest] = edge.value
            self.edge_list.append(edge)
            self.num_edges += 1
            # print "edge source: " + str(edge.source)

    def set_node(self, node):
        self.tasks.append(node)

    def set_proc(self, proc):
        self.processors.append(proc)

    def reset(self):
        self.total_energy = 0
        # self.total_exec_time = 0
        self.task_queue = []


class ProcComb:
    "This class is used to select certain processors from a pool"

    def __init__(self, num_proc):
        self.num_proc = num_proc
        self.proc = []  # stores processor number in order
        self.speed = []  # stores corresponding speed number

    def set_proc(self, p_num, f_num):
        self.proc.append(p_num)
        self.speed.append(f_num)


class CombGen:
    """This class generates all possible combinations of processors and speeds
    Usage:  cg = CombGen(g)  --->(g is the Digraph class found in data.py)
                all_comb = cg.proc_comb() --->(Returns list of ProcComb of all combinations)
                cg.all_speeds ---> List of all combinations in the form [0, 1, 0,3] Where '0' represents
                                            processors not used and ints 1 and 3 are processor speeds
                                            Position of the integer denotes status of particular processor
                                            In the example Processors 0 and 2 are switched off"""

    def __init__(self, g):
        """Pass Digraph g to initialize. g should be ready for computation"""
        # @type self.g Digraph
        self.g = g
        self.p = []
        for i in range(g.num_processors):
            self.p.append(i)
        self.all_combinations = []
        self.all_speeds = []

    def combination(self, seq, length):
        """Algorithm used to generate different processor combinations"""
        if not length:
            return [[]]
        else:
            l = []
            for i in range(len(seq)):
                for result in self.combination(seq[i + 1:], length - 1):
                    l += [[seq[i]] + result]
            return l

    def proc_comb(self):
        """Algorithm used to generate processor comb as well as speeds"""
        for p in range(2, self.g.num_processors + 1):
            # @type pc ProcComb
            l = self.combination(self.p, p)
            # print l
            for comb in l:
                self.speed_comb(comb)
        return self.all_combinations

    def speed_comb(self, comb):
        """Generates the speed combinations for the processor combination passed to it
        in the list 'comb'"""
        speeds = [0] * len(self.g.processors)
        count = 0
        self.next_comb(count, comb, speeds)

    def next_comb(self, count, comb, speeds):
        """Recursive function used in function speed_comb"""
        if (count < len(comb)):
            for x in range(self.g.processors[comb[count]].speeds):
                speeds[comb[count]] = x + 1
                count += 1
                self.next_comb(count, comb, speeds)
                count -= 1
        if (count == len(comb)):
            # print 'speeds : ' + str(speeds)
            speed_cpy = copy.deepcopy(speeds)
            self.all_speeds.append(speed_cpy)
            pc = ProcComb(len(comb))
            pc.proc = comb
            for sp in pc.proc:
                pc.speed.append(speeds[sp] - 1)
            # print str(pc.proc) + '   ' + str(pc.speed)
            self.all_combinations.append(pc)


if __name__ == "__main__":
    pc = ProcComb(3)
    pc.set_proc(0, 2)
    pc.set_proc(1, 2)
    pc.set_proc(2, 3)
    # print "main"
    #data = TaskGraphData()
    #dat = DatHandler()
    # dat.set_path('/home/hparikh/Desktop/Research/Rashad/example_case1.dat')
    #data = dat.read_dat()
    #tg = TGFFGenerator(data, 'example_case1')
    # tg.write_file()
    #tc = TGFFcommand('example_case1')

    g = Digraph(10, 3)
    #tp = TGFFParser(data, 'example_case1', g)
    #g = tp.parse_tgff()
    cg = CombGen(g)
    all_combinations = cg.proc_comb()
