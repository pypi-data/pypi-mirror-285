from deap import base, creator, tools
import random
import numpy as np
import array
from setga import utils

class WrongType(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def weighted_random_choice(weights):
    # Compute the cumulative distribution function (CDF)
    cum_weights = np.cumsum(weights/np.sum(weights))
    def random_numbers(size):
        # Generate random numbers uniformly in [0, 1)
        random_values = np.random.rand(size)
        # Find the indices where random values fall in the CDF
        indices = np.searchsorted(cum_weights, random_values)
        return indices  # Add 1 to convert indices to numbers starting from 1
    return random_numbers

def cxWeightedUniform(ind1, ind2,cx_rate,generator):
    """Executes a weighted uniform crossover that modifies in place the two
    sequence individuals.

    The attributes are swapped according to the *weights* probability.

    :param ind1: The first individual participating in the crossover.
    :type ind1: list
    :param ind2: The second individual participating in the crossover.
    :type ind2: list
    :param weights: List of weights for each attribute to be exchanged.
                    The higher the weight, the more probable the exchange.
    :type weights: list
    :returns: A tuple of two individuals.
    :rtype: tuple

    This function uses the :func:`numpy.random.choice` function from the numpy
    library.
    """
    num_cross = int(len(ind1) * cx_rate)
    crossover_indices = generator(num_cross)
    for i in crossover_indices:
        ind1[i], ind2[i] = ind2[i], ind1[i]

    return ind1, ind2

def cxUniform(ind1, ind2,cx_rate,generator):
    """Executes a weighted uniform crossover that modifies in place the two
    sequence individuals.

    The attributes are swapped according to the *weights* probability.

    :param ind1: The first individual participating in the crossover.
    :type ind1: list
    :param ind2: The second individual participating in the crossover.
    :type ind2: list
    :param weights: List of weights for each attribute to be exchanged.
                    The higher the weight, the more probable the exchange.
    :type weights: list
    :returns: A tuple of two individuals.
    :rtype: tuple

    This function uses the :func:`numpy.random.choice` function from the numpy
    library.
    """
    num_cross = int(len(ind1) * cx_rate)
    crossover_indices = generator(num_cross)
    for i in crossover_indices:
        ind1[i], ind2[i] = ind2[i], ind1[i]

    return ind1, ind2

# Create a closure with fixed weights
def mutWeightedFlipBit(individual, mutation_rate,generator):
    """Mutate the input individual by flipping the value of its attributes based on weighted probabilities for each index.

    The `individual` is expected to be a sequence, and the values of the attributes shall stay valid after the `not` operator is called on them. The overall mutation rate is preserved.

    :param individual: list
        Individual to be mutated.
    :type individual: list
    :param weights: list
        List of weights for each index of the individual. The higher the weight, the more probable the mutation.
    :type weights: list
    :param mutation_rate: float
        Overall mutation rate for the individual.
    :type mutation_rate: float

    :returns:
        tuple
            A tuple containing the mutated individual.

    :notes:
        This function uses the `numpy.random.choice` function from the numpy library to select indices based on their weights and mutates them with the specified mutation rate.
    """
    # Calculate the number of mutations based on the mutation rate
    num_mutations = int(len(individual) * mutation_rate)

    # Select indices to mutate based on weights
    indices_to_mutate = generator(num_mutations)

    # Mutate selected indices
    for i in indices_to_mutate:
        individual[i] = type(individual[i])(not individual[i])

    return individual,

def mutFlipBit(individual, mutation_rate,generator):
    """Mutate the input individual by flipping the value of its attributes based on weighted probabilities for each index.

    The `individual` is expected to be a sequence, and the values of the attributes shall stay valid after the `not` operator is called on them. The overall mutation rate is preserved.

    :param individual: list
        Individual to be mutated.
    :type individual: list
    :param weights: list
        List of weights for each index of the individual. The higher the weight, the more probable the mutation.
    :type weights: list
    :param mutation_rate: float
        Overall mutation rate for the individual.
    :type mutation_rate: float

    :returns:
        tuple
            A tuple containing the mutated individual.

    :notes:
        This function uses the `numpy.random.choice` function from the numpy library to select indices based on their weights and mutates them with the specified mutation rate.
    """
    # Calculate the number of mutations based on the mutation rate
    num_mutations = int(len(individual) * mutation_rate)
    # Select indices to mutate based on weights
    indices_to_mutate = generator(num_mutations)
    # Mutate selected indices
    for i in indices_to_mutate:
        individual[i] = type(individual[i])(not individual[i])
    return individual,



def run_minimizer(set_size,eval_ind, stats_by,stats_names,mutation_rate = 0.001,crossover_rate = 0.02, 
                  pop_size = 150, num_gen = 50000, num_islands = 6, mutation = "bit_flip" , 
                  crossover =  "uniform_partialy_matched", selection = "SPEA2",frac_init_not_removed = 0.01,
                  create_individual_funct = None, ref_points = None, end_mut = None, min_max = None, verbose = True,stop_after = 200, weights = None):
    """Run minimizer algorithm to optimize individual solutions.

    :param set_size: int
        Size of the set to be optimized.
    :param evaluate_individual: function
        Function to evaluate a single individual.
    :param eval_func_kwargs: dict
        Keyword arguments for evaluate_individual function.
    :param mutation_rate: float
        Mutation rate for the algorithm.
    :param crossover_rate: float
        Crossover rate for the algorithm.
    :param pop_size: int
        Population size of the one island of the GA.
    :param num_gen: int
        Maximum number of generations.
    :param num_islands: int
        Number of islands for the algorithm.
    :param mutation: str or callable
        Type of mutation ["bit_flip","inversion"] (see DEAP documentation) or a custom function with two input arguments (array for an individual).
    :param crossover: str or callable
        Type of crossover ["uniform", "onepoint","twopoint","partialy_matched","ordered","uniform_partialy_matched"] (see DEAP documentation) or a custom function with two input arguments (ind1 array and ind2 array).
    :param selection: str
        Type of selection ["SPEA2","NGSA2"] (see DEAP documentation).
    :param frac_init_not_removed: float
        Fraction of initially not removed elements.
    :param create_individual_funct: function
        Function to create an individual.
    :param create_individual_func_kwargs: dict
        Keyword arguments for create_individual_funct.

    :returns:
        np.array(pop) : numpy array
            Final population (array of binary arrays, 1 for every selected item in the set).
        pareto_front : list
            Pareto front solutions (just the solutions, that are Pareto dominant).

    """
    for arg in [mutation_rate, crossover_rate, frac_init_not_removed]:
        if not isinstance(arg, float):
            raise TypeError(f"{arg} must be a float.")

    for arg in [set_size, pop_size, num_gen, num_islands]:
        if not isinstance(arg, int):
            raise TypeError(f"{arg} must be an integer.")
    if isinstance(stats_names, str):
        stats_names = [stats_names]

    def create_individual(set_size,frac_init_not_removed):
        a =  round(set_size*frac_init_not_removed)
        b = round(set_size*frac_init_not_removed*3)
        individual = array.array("b",random.choices([1,0], weights=(1, random.randint(a,b)), k=set_size))
        return creator.Individual(individual)
    
    def evaluate_individual(individual,**kwargs):
        fit = eval_ind(individual,**kwargs)
        individual = np.array(individual)
        len_individual = np.sum(individual)

        if isinstance(fit, list):
            return (len_individual, *fit)
        else:
            return (len_individual, fit)
    

    def get_uniform_reference(num_points):
        y_values = np.linspace(0, 1, num_points)
        # Calculate corresponding y values such that the sum of x and y is 1
        x_values = 1 - y_values

        # Create the numpy array with two columns
        return np.column_stack((x_values, y_values))
    
    
    gen_uniform = weighted_random_choice(np.ones(set_size))
    
    if min_max is None:
        creator.create("Fitness", base.Fitness, weights=(-1,) + (-1,)* (len(stats_names)))     
    else:
        creator.create("Fitness", base.Fitness, weights=(-1,) + min_max)  

    creator.create("Individual", array.array,typecode='b', fitness=creator.Fitness)
    toolbox = base.Toolbox()
    if create_individual_funct == None:
        toolbox.register("individual", create_individual, set_size = set_size, frac_init_not_removed = frac_init_not_removed)
    else:
        toolbox.register("individual", create_individual_funct)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate_individual)
    if mutation == "bit-flip":       
        toolbox.register("mutate_low", mutFlipBit, mutation_rate=mutation_rate, generator = gen_uniform)
        toolbox.register("mutate_high", mutFlipBit, mutation_rate=mutation_rate*10, generator = gen_uniform)
        mut_functs = [toolbox.mutate_high if i+1 < num_islands * 0.5 else toolbox.mutate_low for i in range(num_islands)]
    if mutation == "inversion":
        mut_functs = [tools.mutInversion] * num_islands

    if mutation == "bit-flip_old":
        toolbox.register("mutate_low", tools.mutFlipBit, indpb=mutation_rate/2)
        toolbox.register("mutate_high", tools.mutFlipBit, indpb=mutation_rate)
        mut_functs = [toolbox.mutate_high if i+1 < num_islands * 0.5 else toolbox.mutate_low for i in range(num_islands)]
    if mutation == "weighted":
        if weights is None:
            raise WrongType("weights cannot be None")
        generate_random_numbers = weighted_random_choice(weights)
        toolbox.register("mutate", mutWeightedFlipBit, mutation_rate = mutation_rate, generator = generate_random_numbers)
    if callable(mutation):
        mut_functs = [mutation] * num_islands
    if type(mutation) == list:
        mut_functs = mutation
        for i,mut in enumerate(mut_functs):
            if mut == "bit-flip":
                toolbox.register("mutate_flip", mutFlipBit, mutation_rate=mutation_rate, generator = gen_uniform)
                mut_functs[i] = toolbox.mutate_flip
            elif mut == "inversion":
                mut_functs[i] = tools.mutInversion
            elif mut == "weighted":
                if weights is None:
                    raise WrongType("weights cannot be None")
                generate_random_numbers = weighted_random_choice(weights)
                toolbox.register("mutate_weighted", mutWeightedFlipBit, mutation_rate = mutation_rate, generator = generate_random_numbers)
                mut_functs[i] = toolbox.mutate_weighted
            else:
                raise WrongType("unknown type of mutation in the list")



    if mutation not in ["bit-flip","inversion", "weighted","bit-flip_old"] and not callable(mutation) and not type(mutation) == list:
        raise WrongType("Unknown type of mutation")

    if crossover == "uniform":
        toolbox.register("mate", cxUniform,cx_rate=crossover_rate,generator = gen_uniform)
    if crossover == "uniform_old":
        toolbox.register("mate", tools.cxUniform,indpb=crossover_rate)
    if crossover == "onepoint":
        toolbox.register("mate", tools.cxOnePoint)
    if crossover == "twopoint":
        toolbox.register("mate", tools.cxTwoPoint)
    if crossover == "partialy_matched":
        toolbox.register("mate", tools.cxPartialyMatched)
    if crossover == "uniform_partialy_matched":
        toolbox.register("mate", tools.cxUniformPartialyMatched,indpb=crossover_rate)
    if crossover == "ordered":
        toolbox.register("mate", tools.cxOrdered)
    if crossover == "weighted":
        if weights is None:
            raise WrongType("weights cannot be None")
        generate_random_numbers = weighted_random_choice(weights)
        toolbox.register("mate", cxWeightedUniform, cx_rate = crossover_rate, generator = generate_random_numbers)
    if callable(crossover):
        toolbox.register("mate", crossover)
    if crossover not in ["uniform", "onepoint","twopoint","partialy_matched","ordered","uniform_partialy_matched","weighted","uniform_old"] and not callable(crossover):
        raise WrongType("Unknown type of crossover")

    if selection == "SPEA2":
        toolbox.register("select", tools.selSPEA2)
    if selection == "NSGA2":
        toolbox.register("select", tools.selNSGA2)
    if selection == "NSGA3":      
        if ref_points is None:
            ref_points = get_uniform_reference(pop_size * 0.1)
        toolbox.register("select", tools.selNSGA3,ref_points = ref_points)
    if selection not in ["SPEA2","NSGA2","NSGA3"]:
        raise WrongType("Unknown type of mating")
    
    toolbox.register("migrate",tools.migRing,k=10,selection = toolbox.select)

    stats = tools.Statistics()

    for i,s in enumerate(["Num removed"] + stats_names):
        stats.register(s, lambda x, i=i, stats_by=stats_by: (sorted(x, key=lambda ind: (ind.fitness.values[stats_by], ind.fitness.values[0]))[0].fitness.values[i]))
    

    islands = [toolbox.population(n=pop_size) for _ in range(num_islands)]
    population, logbook, gens, best_sols = utils.eaMuPlusLambda_stop_isl(islands,toolbox, mu=round(len(islands[0])), num_ind = len(islands[0]),cxpb=0.45, mutpb=0.45, ngen=num_gen, mut_functs_isl=mut_functs,stats=stats, verbose=verbose, end_mut = end_mut,stop_after = stop_after)

    pop = [solution for island in population for solution in island]

    pareto_front = tools.sortNondominated(pop, k=pop_size*num_islands,first_front_only=True)
    return pop,pareto_front,gens,logbook,best_sols