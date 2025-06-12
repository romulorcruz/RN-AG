import random as rd
from typing import List, TypeVar, Generic, Any, Sequence

T = TypeVar('T')

class Gene(Generic[T]):
    def __init__(self, possibilities: List[T]):
        self.value: T = rd.choice(possibilities)

class Individue(Generic[T]):
    def __init__(self, size: int, possibilities: List[T]):
        self.genes: List[Gene[T]] = [Gene(possibilities) for _ in range(size)]
        self.fitness: Any = None

    def get_values(self) -> List[T]:
        return [gene.value for gene in self.genes]

class Population(Generic[T]):
    def __init__(self, size: int, n_genes: int, possibilities: List[T]):
        self.individues: List[Individue[T]] = [Individue(n_genes, possibilities) for _ in range(size)]
        self.fitness: List[Any] = []

    def get_fitness(self, type: str, key: List[str]):
        if type == 'password':
            self.fitness = pop_password_fitness(self, key)

def objetive_function_password_length(password_len: int, shot_len: int):
    return password_len - shot_len

def objetive_function_password_shot(password: Sequence[str], shot: Sequence[str]):
    '''
        Objective function for a password problem.

        :param password: Sequence of characters of the correct password
        :param shot: Sequence of characters of the attempted password
    '''
    distance = 0
    for char_password, char_shot in zip(password, shot):
        distance += abs(ord(char_password) - ord(char_shot))
    return distance

def generate_population(possibilities: List[T], p_size: int, n_genes: int) -> Population[T]:
    '''
        Generate a population of individuals.

        :param possibilities: Possible values that a gene can assume
        :param p_size: Number of individuals in the population
        :param n_genes: Number of genes in an individual
    '''
    return Population(p_size, n_genes, possibilities)

def pop_password_fitness_count(population: Population[T], password_len: int):
    '''
        Get the fitness of a population for the password problem by the length.

        :param population: The Population object of ints to check for fitness
        :param password: Length of the password
    '''

    fitness_list: List[int] = []
    for individue in population.individues:
        value = individue.get_values()[0]  
        fitness = abs(password_len - value)
        individue.fitness = fitness
        fitness_list.append(fitness)
    return fitness_list

def pop_password_fitness(population: Population[T], password: Sequence[str]):
    '''
        Get the fitness of a population for the password problem by the difference of characteres.

        :param population: The Population object to check for fitness
        :param password: Sequence of characters of the correct password
    '''
    fitness_list: List[int] = []
    for individue in population.individues:
        values = individue.get_values()
        str_values = [str(v) for v in values]
        fitness = objetive_function_password_shot(password, str_values)
        individue.fitness = fitness
        fitness_list.append(fitness)
    return fitness_list

###############################################################################
#                                  Crossing                                   #
###############################################################################

from typing import Tuple

def uniform_crossover(father: Individue[T], mother: Individue[T], c_rate: float) -> Tuple[Individue[T], Individue[T]]:
    '''
        Generate two sons of an uniform crossing.

        :param father Individue: The first parent individual.
        :param mother Individue: The second parent individual.
        :param c_rate float: The crossing rate
    '''
    if rd.random() < c_rate:
        son1_genes: List[Gene[T]] = []
        son2_genes: List[Gene[T]] = []
        for g_f, g_m in zip(father.genes, mother.genes):
            if rd.random() < 0.5:
                son1_genes.append(Gene([g_f.value]))
                son2_genes.append(Gene([g_m.value]))
            else:
                son1_genes.append(Gene([g_m.value]))
                son2_genes.append(Gene([g_f.value]))
        son1 = Individue[T](0, [])
        son2 = Individue[T](0, [])
        son1.genes = son1_genes
        son2.genes = son2_genes
        return son1, son2
    return father, mother

###############################################################################
#                                  Selectioning                               #
###############################################################################

def roulete_selectioning(population: Population[T], fitness: List[int], p_size: int) -> List[Individue[T]]:
    '''
        Roulette wheel selection for individuals.
    '''
    if all(f == 0 for f in fitness):        
        return rd.choices(population.individues, k=p_size)
    selected = rd.choices(population.individues, weights=fitness, k=p_size)
    return selected

def tournment_selectioning(population: Population[T], fitness: List[int], p_size: int, tourn_size: int = 2) -> List[Individue[T]]:
    '''
        Tournament selection for individuals.
    '''
    selected: List[Individue[T]] = []
    for _ in range(p_size):
        competitors = rd.sample(population.individues, tourn_size)
        winner = competitors[0]
        for ind in competitors[1:]:
            if ind.fitness < winner.fitness:
                winner = ind
        selected.append(winner)
    return selected

###############################################################################
#                                  Mutation                                   #
###############################################################################

def mutation(population: Population[T], m_chance: float, possibilities: List[T]):
    for individue in population.individues:
        if rd.random() < m_chance:
            gene_i = rd.randint(0, len(individue.genes) - 1)
            current_value = individue.genes[gene_i].value
            temp = [x for x in possibilities if x != current_value]
            individue.genes[gene_i].value = rd.choice(temp)