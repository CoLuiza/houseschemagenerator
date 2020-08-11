import abc
import random


class GeneticAlgorithm(abc.ABC):
    def __init__(self, no_generations, no_chromosomes, mutation_rate=0.1, mutation_area=0.1, size_of_chromosomes=100):
        self.no_generations = no_generations
        self.no_chromosomes = no_chromosomes
        self.size_of_chromosomes = size_of_chromosomes
        self.mutation_rate = mutation_rate
        self.mutation_area = mutation_area
        self.rand = random.SystemRandom()

    @abc.abstractmethod
    def mutate(self, chromosome):
        pass

    @abc.abstractmethod
    def crossover(self, chromosome1, chromosome2):
        pass

    @abc.abstractmethod
    def get_fitness(self, chromosome):
        pass

    @abc.abstractmethod
    def get_random_chromosome(self):
        pass

    def choose_one(self, chromosomes):
        chosen_range_number = self.rand.randrange(1, sum(range(len(chromosomes) + 1)))
        chosen = 0
        while chosen_range_number > 0:
            chosen += 1
            chosen_range_number -= chosen
        return chromosomes[chosen - 1]

    def make_new_generation(self, chromosomes1, chromosomes2):
        chromosomes1.sort(key=lambda x: self.get_fitness(x))
        chromosomes2.sort(key=lambda x: self.get_fitness(x))
        best_count = int(50 / 100 * self.no_chromosomes)
        chromosomes = list()
        for i in range(1, best_count + 1):
            chromosomes.append(chromosomes1[self.no_chromosomes - i])
            chromosomes.append(chromosomes2[self.no_chromosomes - i])
        return chromosomes + self.rand.sample(chromosomes1 + chromosomes2, self.no_chromosomes - 2 * best_count)

    def run(self):
        chromosomes = [self.get_random_chromosome() for _ in range(self.no_chromosomes)]
        for _ in range(self.no_generations):
            new_chromosomes = [self.get_random_chromosome() for _ in range(self.no_chromosomes)]
            chromosomes = self.make_new_generation(chromosomes, new_chromosomes)
            for _ in range(1):
                chromosome_mother = self.choose_one(chromosomes)
                chromosome_father = self.choose_one(chromosomes)
                chromosome_child = self.crossover(chromosome_mother, chromosome_father)
                to_be_mutated = self.mutation_rate >= self.rand.random()
                if to_be_mutated:
                    chromosome_child = self.mutate(chromosome_child)
                if self.get_fitness(chromosome_child) > self.get_fitness(chromosomes[0]):
                    chromosomes[0] = chromosome_child
        chromosomes.sort(key=lambda x: self.get_fitness(x))
        return chromosomes[-1]
