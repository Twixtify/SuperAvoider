import random
import numpy as np
import matplotlib.pyplot as plt


def is_numpy(ind):
    """
    Check if ind is a numpy array
    :param ind: Array representing the individual
    :return: Boolean
    """
    if type(ind) is np.ndarray:
        return True
    else:
        return False


def sort_lists(list1, list2, descending=True):
    """
    If descending = True:
        Sort list1 in descending order (largest-to-smallest value)
        and each element of list2 is mapped to list1 elements
    If descending = False:
        Same as above but instead sort in ascending order (smallest-to-largest sorting)
    :param list1: List
    :param list2: List
    :param descending: Boolean
    :return: Sorted lists
    """
    sorted_list1, sorted_list2 = (list(t) for t in zip(*sorted(zip(list1, list2), reverse=descending)))
    return sorted_list1, sorted_list2


def unique_list(list1, list2):
    """
    Return unique elements of list1, i.e return elements of list1 that is not in  list2.
    :param list1: List
    :param list2: List
    :return: List
    """
    unique_list1 = list(set(list1).difference(list2))
    return unique_list1


def map_to_interval(t, old_range, new_range):
    """
    Map a number 't' in a range 'old_range' to a new interval 'new_range'
    1) First, apply the map t ↦ t−a so the left endpoint shifts to the origin. The image interval is [0,b−a].
    2) Next scale the interval to unit length by dividing by its length
    (this is the only place the requirement a≠b is needed).
    The map that does this is t↦1/(b−a)*t. The image interval is [0,1].
    3) Scale up by the desired length d−c using the map t↦(d−c)⋅t, and the image is [0,d−c].
    4) Finally shift the left endpoint to c by the map. t↦c+t. The image is [c,d].
    :param t: Float
    :param old_range: List
    :param new_range: List
    :return: Float
    """
    return new_range[0] + (new_range[1] - new_range[0]) / (old_range[1] - old_range[0]) * (t - old_range[0])

# ---------------------------------------------------------------------------------------------------------------------


def co_uniform(ind1, ind2, co_prob=0.5):
    """
    Uniform crossover. Each individual keep their length.
    Note that this method modify the incoming lists.
    :param ind1: Array of genome 1
    :param ind2: Array of genome 2
    :param co_prob: Double
    :return: Input arrays
    """
    size = min(len(ind1), len(ind2))
    co_ind1, co_ind2 = [], []
    # Iterate over the smallest individual
    for gene in range(size):
        if np.random.random() < co_prob:
            co_ind1.append(ind2[gene])
            co_ind2.append(ind1[gene])
        else:
            co_ind1.append(ind1[gene])
            co_ind2.append(ind2[gene])
    # This assignment works for both numpy arrays and lists
    ind1[:size] = co_ind1
    ind2[:size] = co_ind2
    return ind1, ind2


def co_one_point(ind1, ind2):
    """
    One point crossover.
    Note that if len(ind1) != len(ind2) then the length of the output arrays will be interchanged.
    Unlike co_uniform this method does not work with references
    :param ind1: List or numpy array
    :param ind2: List or numpy array
    :return: Lists or numpy arrays
    """
    size = min(len(ind1), len(ind2))
    co_point = np.random.randint(1, size - 1)  # pick crossover point between first and last element
    """ 
    Since numpy arrays are fixed in size we have to convert them to lists first.
    This is necessary since individuals 1 and 2 might be of different lengths.
    """
    # print(co_point)
    # print("Input:", ind1, ind2)
    if is_numpy(ind1) and is_numpy(ind2):
        ind1, ind2 = ind1.tolist(), ind2.tolist()
        co_ind1, co_ind2 = ind1[:co_point] + ind2[co_point:], ind2[:co_point] + ind1[co_point:]
        ind1, ind2 = np.array(co_ind1), np.array(co_ind2)
    else:
        co_ind1, co_ind2 = ind1[:co_point] + ind2[co_point:], ind2[:co_point] + ind1[co_point:]
        ind1, ind2 = co_ind1, co_ind2
    # print("Output:", ind1, ind2)
    # print("Lengths: Input (%i, %i) Output: (%i, %i)" % (len(ind1), len(ind2), len(co_ind1), len(co_ind2)))
    return ind1, ind2

# ---------------------------------------------------------------------------------------------------------------------


def sel_best(fitness, size):
    """
    Return list of indexes with length 'size' in descending order [from best to worst]
    :param fitness: List
    :param size: Integer
    :return: List
    """
    fitness_index = []
    for i, _ in enumerate(fitness):
        fitness_index.append(i)
    sorted_fitness, sorted_index = sort_lists(fitness, fitness_index, descending=True)
    return [sorted_index[k] for k in range(size)]


def sel_worst(fitness, size):
    """
    Return list of indexes with length 'size' in ascending order [from worst to best]
    :param fitness: List
    :param size: Integer
    :return: List
    """
    fitness_index = []
    for i, _ in enumerate(fitness):
        fitness_index.append(i)
    sorted_fitness, sorted_index = sort_lists(fitness, fitness_index, descending=False)
    return [sorted_index[k] for k in range(size)]


def sel_random(individuals, size, replacement=False):
    """
    Return list of size k with randomly selected individuals
    :param individuals: List of objects
    :param size: Integer, returned list length
    :param replacement: Boolean
    :return: List of individuals
    """
    if is_numpy(individuals):
        return [np.random.choice(individuals, replace=replacement) for _ in range(size)]
    else:
        if replacement:
            return [random.choice(individuals) for _ in range(size)]
        else:
            return random.sample(individuals, size)


def sel_roulette(fitness, tournaments=2, replace=False):
    # TODO: Add 'replace' variable
    """
    Fitness proportionate selection or roulette wheel selection.
    :param fitness: List of fitness values
    :param tournaments: Integer, number of tournaments to hold
    :param replace: Boolean, draw with replacement
    :return: List of selected indexes
    """
    # Create list of indexes
    fitness_index = []
    for i, _ in enumerate(fitness):
        fitness_index.append(i)
    # Sort fitness in descending order
    fitness, fitness_index = sort_lists(fitness, fitness_index, descending=True)
    # Normalize with regard to total fitness
    tot_fitness = sum(fitness)
    fitness[:] /= tot_fitness
    # Draw individuals
    sel_individuals = []
    for tournament in range(tournaments):
        tmp, rand = 0, np.random.random()
        for j, val in enumerate(fitness):
            tmp += val
            if rand < tmp:
                sel_individuals.append(fitness_index[j])
                break
    print(fitness, fitness_index)
    print(sel_individuals)
    return sel_individuals


def sel_tournament(fitness, tournaments=1, tour_size=2, replace=False):
    """
    Tournament selection.
    :param fitness: List of fitness
    :param tour_size: Number of individuals participating in each tournament
    :param tournaments: Integer, number of tournaments held (if replace=True, then tournaments <= len(fitness) - 1
    :param replace: Boolean, should selected individuals be drawn with replacement
    :return: List of indexes that survive.
    """
    # List of indexes
    # fitness_index = np.arange(len(fitness)).tolist()
    tmp_index, tmp_fitness = [], []
    for i, val_1 in enumerate(fitness):
        tmp_index.append(i)
        tmp_fitness.append(val_1)
    # Optional sorting
    #fitness, fitness_index = sort_lists(fitness, fitness_index)
    # Perform tournament
    sel_individuals = []
    #print("Initial fitness:", fitness)
    for tournament in range(tournaments):
        tour_individuals = sel_random(tmp_fitness, tour_size, replacement=False)
        # Select best individual from tournament individuals
        best_ind = max(tour_individuals)
        # Append corresponding index of best performing individual to selected individuals
        for i, val_2 in enumerate(tmp_fitness):
            if val_2 == best_ind:
                sel_individuals.append(tmp_index[i])
                break
        # Using replacement
        if replace is False:
            del tmp_index[tmp_fitness.index(best_ind)]
            del tmp_fitness[tmp_fitness.index(best_ind)]
            #print("Fitness: %s removed: %s" % (fitness, best_ind))
        #print("Tournament %s. Individuals %s. Winner %s." % (tournament, tour_individuals, best_ind))
    #print("Winning individuals (by index):", sel_individuals)
    return sel_individuals

# ---------------------------------------------------------------------------------------------------------------------


def mut_uniform(ind, range_max, range_min, prob=0.01):
    """
    Mutate an individual
    :param ind: List of values
    :param range_max: Float, maximum constraint
    :param range_min: Float, minimum constraint
    :param prob: Double, Mutation rate
    :return: List
    """
    for i, val in enumerate(ind):
        if random.random() <= prob:
            ind[i] = range_min + (range_max - range_min) * random.random()
    print(ind)
    return ind


def mut_gauss(ind, mut_prob, perturb_size=1.):
    """
    Mutate an individual using a Gaussian distribution
    :param ind: List of values
    :param mut_prob: Float, probability for mutation
    :param perturb_size: Float, size of perturbation
    :return: List
    """
    for i, val in enumerate(ind):
        if random.random() <= mut_prob:
            ind[i] = val + perturb_size * random.gauss(0, 1)
    return ind

# ---------------------------------------------------------------------------------------------------------------------


def breed(individuals, fitness, sel_method, co_method, mut_method, *args):
    # ------- Convert numpy array to list -------
    ind_indexes = []
    for i, individual in enumerate(individuals):
        ind_indexes.append(i)
#        print("Individual", i, individual)
        if is_numpy(individual):
            individuals[i] = individual.tolist()
    if is_numpy(fitness):
        fitness = fitness.tolist()

    #############################################

    # ---------- Selection ----------
    # Note len(parents) = tournaments
    parents = sel_method(fitness=fitness, tournaments=args[0], tour_size=args[1], replace=False)
    not_parents = unique_list(ind_indexes, parents)
#    print("Winning individuals (by index):", parents)
    #################################

    # ---------- Breed parents with population ----------

    # -- Elitism variables --
    worst_id = sel_worst(fitness, 1)[0]
    best_ind = list(individuals[sel_best(fitness, 1)[0]])
    #########################

    # -- Perform Crossover --
    random.shuffle(not_parents)
    children = ()
    for i, val in enumerate(not_parents):
        if i < len(parents):
            co_method(individuals[val], individuals[parents[i]])
            children += (val, parents[i])
#            print("Crossover performed on: (", val, ",", parents[i], ")")
#    [print("Child %i %s" % (child, individuals[child])) for child in children]
    #########################

    #####################################################
    # ------- Mutate children -------
    perturb_size = 1 #/ map_to_interval(np.mean(fitness), [0, 1000], [0, 1])
#    print("Mean fitness", mean_fitness, "Perturbation size", perturb_size)
    for child in children:
        mut_prob = 1. / len(individuals[child])  # Average 1 mutation per child
        mut_method(individuals[child], mut_prob, perturb_size)
    #########################################
#    [print("Individual %i %s" % (i, individual)) for i, individual in enumerate(individuals)]
    # -- Replace worst individual with the best individual
    individuals[worst_id] = best_ind
    return individuals


class SuperAvoiderGA:
    def __init__(self):
        print()


def test_stuff():
    x_row, x_col = 10, 100000
    x = np.ones((x_row, x_col))
    for _ in range(x_row):
        x[_, 0] = random.choice([-1, 1]) * random.random()
    for val in range(x_row):  # Matrix row
        for gen in range(x_col):  # Generation
            if gen > 0:
                x[val, gen] = x[val, gen - 1] + random.gauss(0, 1) / np.sqrt(gen + 1)
    for i in range(x_row):
        print("max:", np.max(x[i, :]) / x[i, 0], " \t", "min:", np.abs(np.min(x[i, :])) / x[i, 0])
        print("Change:", np.abs(x[i, len(x[i, :]) - 1] - x[i, 0]))
        print("Init:", x[i, 0], "Mean:", np.mean(x[i, :]), "Std:", np.std(x[i, :]), "\n")
        # print(x)
    fig, ax = plt.subplots(nrows=2, ncols=5)
    tmp_row, tmp_col, tmp = 0, 0, 0
    for row in ax:
        for col in row:
            col.plot(x[tmp, :])
            ax[tmp_row, tmp_col].text(len(x[tmp, :]), x[tmp, 0], str(tmp))
            tmp_col += 1
            tmp += 1
        tmp_col = 0
        tmp_row += 1
    plt.show()


if __name__ == '__main__':
    SA_GA = SuperAvoiderGA()
    x1 = np.arange(0, 5)
    x2 = np.arange(5, 10)
    print("%s\n%s\n" % (x1, x2))
    sel_tournament(fitness=x2.tolist(), tournaments=2, tour_size=2, replace=False)











    population = []
    score = np.random.random_integers(0, 20, 10)
    for indi in range(10):
        population.append(np.arange(indi, indi + 4))
    print("Fitness:", score)

    steps = 1000
    tmp = np.zeros((len(population), 4, steps))
    for _ in range(steps):
        tmp_list = breed(population, score, sel_tournament, co_uniform, mut_gauss, 4, 3)
        score[:] += random.random()
        for individual, ind_list in enumerate(tmp_list):
            for i, val in enumerate(ind_list):
                tmp[individual, i, _] = val

    mean_list = np.mean(tmp, axis=2)
    std_list = np.std(tmp, axis=2)
    print("Mean:", mean_list)
    print("Std:", std_list)

    fig, ax = plt.subplots(nrows=2, ncols=5)
    tmp_row, tmp_col, tmp1 = 0, 0, 0
    for row in ax:
        for col in row:
            col.plot(tmp[tmp1, 0, :], 'r-',
                     tmp[tmp1, 1, :], 'b-',
                     tmp[tmp1, 2, :], 'g-',
                     tmp[tmp1, 3, :], 'k-')
            ax[tmp_row, tmp_col].text(len(tmp[tmp1, 0, :]), tmp[tmp1, 0, 0], str(tmp1))  # Text at [x,y] position
            tmp_col += 1
            tmp1 += 1
        tmp_col = 0
        tmp_row += 1
    plt.show()
