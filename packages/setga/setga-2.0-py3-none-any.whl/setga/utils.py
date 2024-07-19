import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np 
from deap import tools
import os
#import concurrent.futures
import random


class SolutionException(Exception):
    def __init__(self, message):
        super().__init__(message)
        
# same as in the DEAP library except for enabeling different mutations for different islands
def varOr(population, toolbox, num_ind, cxpb, mutpb,mutate_funct):
    """Part of an evolutionary algorithm applying only the variation part
    (crossover **and** mutation). The modified individuals have their
    fitness invalidated. The individuals are cloned so returned population is
    independent of the input population. Same as in the DEAP library except for enabling 
    different mutations for different islands.

    :param population: array
        List of individuals to vary.
    :type population: list
    :param toolbox: deap.base.Toolbox
        Contains the evolution operators.
    :type toolbox: deap.base.Toolbox
    :param num_ind: int
        The number of children to produce at each generation.
    :type num_ind: int
    :param cxpb: float
        The probability of mating two individuals.
    :type cxpb: float
    :param mutpb: float
        The probability of mutating an individual.
    :type mutpb: float
    :param mutate_funct: function
        Mutation function.
    :type mutate_funct: function

    :returns:
        _array_: A list of varied individuals that are independent of their
                parents.

    """
    assert (cxpb + mutpb) <= 1.0, (
        "The sum of the crossover and mutation probabilities must be smaller "
        "or equal to 1.0.")

    offspring = []
    for _ in range(num_ind):
        op_choice = random.random()
        if op_choice < cxpb:            # Apply crossover
            ind1, ind2 = [toolbox.clone(i) for i in random.sample(population, 2)]
            ind1, ind2 = toolbox.mate(ind1, ind2)
            del ind1.fitness.values
            offspring.append(ind1)
        elif op_choice < cxpb + mutpb:  # Apply mutation
            ind = toolbox.clone(random.choice(population))
            ind, = mutate_funct(ind)
            del ind.fitness.values
            offspring.append(ind)
        else:                           # Apply reproduction
            offspring.append(random.choice(population))

    return offspring


def eaMuPlusLambda_stop_isl(islands, toolbox, mu, num_ind, cxpb, mutpb, ngen,mut_functs_isl: list, stats = None, stop_after = 200, verbose=__debug__, end_mut = None):
    """This is the :math:`(\mu + \lambda)` evolutionary algorithm.

    :param islands: list
        List of arrays of islands.
    :type islands: list
    :param toolbox: deap.base.Toolbox
        Contains the evolution operators.
    :type toolbox: deap.base.Toolbox
    :param mu: int
        The number of individuals to select for the next generation.
    :type mu: int
    :param num_ind: int
        The number of children to produce at each generation.
    :type num_ind: int
    :param cxpb: float
        The probability that an offspring is produced by crossover.
    :type cxpb: float
    :param mutpb: float
        The probability that an offspring is produced by mutation.
    :type mutpb: float
    :param ngen: int
        Number of generations.
    :type ngen: int
    :param mut_functs_isl: list
        List of mutation functions for every island.
    :type mut_functs_isl: list
    :param stats: deap.tools.Statistics, optional
        An object that is updated in place, optional. Defaults to None.
    :type stats: deap.tools.Statistics
    :param stop_after: int, optional
        Number of non-improving generations to stop after. Defaults to 100.
    :type stop_after: int
    :param verbose: str, optional
        Verbose. Defaults to __debug__.
    :type verbose: str
    """
    best_sols = []

    def isl_evaluate(invalid_ind):
        return list(toolbox.map(toolbox.evaluate, invalid_ind))
    
    def isl_select(island):
        return toolbox.select(island, mu)
    
    def isl_evolve(island,i):
        return varOr(island, toolbox, num_ind, cxpb, mutpb,mut_functs_isl[i])
    
    def comp_fitness_inv(island):
        inv_ind = [ind for ind in island if not ind.fitness.valid]
        fitnesses = isl_evaluate(inv_ind)
        for ind, fit in zip(inv_ind, fitnesses):
                ind.fitness.values = fit

    
    def island_evolve(island,i):
        offsprings  = isl_evolve(island,i)
        comp_fitness_inv(offsprings)
        return isl_select(offsprings + island)
    
    def migrate(islands,gen):
        if min([min(islands[i], key=lambda ind: ind.fitness.values[1]).fitness.values[1] for i in range(len(islands))]) > 0:
            if gen%5 == 0:
                toolbox.migrate(islands)
        else:
            if gen%10 == 0:
                toolbox.migrate(islands)

    def should_stop(islands,prev_max_lens,max_len_counter,stop_after):
        max_lens = set([min(islands[i], key=lambda ind: ind.fitness.values[1]).fitness.values[0] for i in range(len(islands))])
        if prev_max_lens == max_lens:
            max_len_counter += 1
        else:
            prev_max_lens = max_lens
            max_len_counter = 1
        if max_len_counter > stop_after:
            return True,prev_max_lens,max_len_counter
        return False,prev_max_lens,max_len_counter
    
    def log_results(islands,gen):
        for i in range(len(islands)):
            record = stats.compile(islands[i]) if stats is not None else {}
            logbook.record(gen=gen, island = i+1, **record)
            if verbose:
                print(logbook.stream)
        best_sols.append(islands[0][np.argmin([ind.fitness.values[1] for ind in islands[0]])])
        if verbose:        
            print("\n")

    logbook = tools.Logbook()
    logbook.header = ['gen'] + ['island'] + (stats.fields if stats else [])

    # Evaluate the individuals with an invalid fitness
    fitnesses = list(map(comp_fitness_inv, islands))

    record = stats.compile(islands[0]) if stats is not None else {}
    logbook.record(gen=0, islands = 0, **record)
    if verbose:
        print(logbook.stream)

    prev_max_len = set()
    max_len_counter = 1
    # Begin the generational process
    for gen in range(1, ngen + 1):
        
        stop,prev_max_len,max_len_counter = should_stop(islands,prev_max_len,max_len_counter,stop_after)   
        if stop:
            break
        # Vary the population
        islands = list(map(island_evolve, islands,range(len(islands))))

        # Update the statistics with the new population
        if gen%10 == 0:
            log_results(islands,gen)
        migrate(islands,gen)    
    
    return islands, logbook, gen, best_sols


def get_sol_from_indices(indices,ind_len):
    """Getting a solution boolean array based on the indices.

    :param indices: np.array
        Indices of selected items.
    :type indices: np.array
    :param ind_len: _type_
        Size of the set.
    :type ind_len: _type_

    :returns:
        np.array
            Returns a solution in the same format as outputted from the optimizer.
    """
    zeros = np.zeros(ind_len)
    zeros[indices] = 1
    return zeros

def get_removed_from_solution(solution,names):
    """Get set items that were not selected by the minimizer.

    :param solution: array
        Minimizer boolean solution.
    :type solution: array
    :param names: np.array
        Names of the items of the list in the correct order.
    :type names: np.array

    :returns:
        np.array
            Set items not selected by minimizer.
    """
    return np.array(names[np.where(solution == 1)[0]])

def plot_pareto(solutons,pareto,upper_bound = None,lower_bound = None):
    """Plots the final solutions outputted by the minimizer.

    :param solutions: np.array
        All final solutions.
    :type solutions: np.array
    :param pareto: np.array
        All solutions on the Pareto front.
    :type pareto: np.array
    :param upper_bound: float, optional
        Upper bound on p-value for selected solutions. Defaults to None.
    :type upper_bound: float, optional
    :param lower_bound: float, optional
        Lower bound on p-value for selected solutions. Defaults to None.
    :type lower_bound: float, optional

    :raises SolutionException:
        Exception when no solution found.

    :returns:
        matplotib.pyplot
            Plotted solutions with Pareto front.
    """
    plt.scatter(solutons[:,0],solutons[:,1],s = 1.5,color='blue', marker='o', label='Solution')
    plt.scatter(pareto[:,0],pareto[:,1],s = 5,color='red', marker='o', label='Front')
    #plt.gca().invert_yaxis()
    #plt.gca().invert_xaxis()

    plt.xlabel('Number of extracted genes')  # X-axis label
    plt.ylabel('p-value')  # Y-axis label

    plt.title('Solution extraction')  # Title

    plt.legend()  # Show legend

    plt.grid(True, linestyle='--', alpha=0.7)  # Add gridlines

    plt.xticks(fontsize=12)  # Customize tick labels
    plt.yticks(fontsize=12)
    selected = solutons[np.logical_and(solutons[:,1] < 0.5,solutons[:,1] >= 0.1)][:,0]
    if len(selected) == 0:
        raise SolutionException("No solution found")
    
    if upper_bound is not None:
        plt.axhline(y=upper_bound, color='red', linestyle='--', linewidth=2)
    if lower_bound is not None:
        plt.axhline(y=lower_bound, color='red', linestyle='--', linewidth=2)
    # Add the Rectangle patch to the current plot¨
    # Save or display the plot
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    # Save the plot as an image
    return plt
    
    #plt.show()



def get_results(solutions,fitness,names,upper_bound = 0.4, lower_bound = 0, min_freq = 0.9):
    """Selecting final set of candidate set items from solutions extracted by the minimizer, by taking solutions that appear often in the best solutions.

    :param solutions: np.array
        All final solutions.
    :type solutions: np.array
    :param fitness: np.array
        Fitness of extracted solutions.
    :type fitness: np.array
    :param names: list
        Names of all set items in the correct order.
    :type names: list
    :param upper_bound: float, optional
        Upper bound on p-value for selected solutions. Defaults to 0.4.
    :type upper_bound: float, optional
    :param lower_bound: float, optional
        Lower bound on p-value for selected solutions. Defaults to 0.
    :type lower_bound: float, optional
    :param min_freq: float, optional
        Minimal frequency for a solution to appear in the set of best solutions to be selected. Defaults to 0.65.
    :type min_freq: float, optional

    :raises SolutionException:
        _description_

    :returns:
        list
            Final set of candidate set items from solutions extracted by the minimizer.
    """
    fitness_filtered = fitness[np.logical_and(fitness[:,1] < upper_bound,fitness[:,1] >= lower_bound)]
    
    #pareto_filtered = pareto
    solutions = solutions[np.logical_and(fitness[:,1] < upper_bound,fitness[:,1] >= lower_bound)]
    sel_sols = solutions
    if len(fitness_filtered) == 0:
        raise SolutionException("No solution found")
    
    sel_sols = np.unique(sel_sols,axis = 0)
    genes = get_removed_from_solution(get_sol_from_indices(np.where(sel_sols.sum(axis=0) >= len(sel_sols)*(min_freq))[0],sel_sols.shape[1]),names)
    return genes