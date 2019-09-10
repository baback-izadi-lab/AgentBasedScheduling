from sklearn.naive_bayes import GaussianNB
import random


class Scheduler:
    def __init__(self, dag, processors, sch_algo, ml_algo):
        self.dag = dag
        self.processors = processors
        self.ml_algo = ml_algo
        self.sch_algo = sch_algo
        self.calculated_schedules = []

    def random(self):
        while self.stopping_condition():
            processor_combo = random.choice(self.processors)
            schedule = self.sch_algo.run(processor_combo, self.dag)
            self.calculated_schedules.append(schedule)

    def stopping_condition(self):
        if len(self.calculated_schedules) == self.processors:
            return False
        else:
            return True

    def train(self, training_data, training_labels, remaining_combos):
        while self.stopping_condition():
            # Train ML classifier using training set
            self.ml_algo.fit(training_data, training_labels)
            # Predict uncalculated combinations
            self.ml_algo.predict(remaining_combos)
