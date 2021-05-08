from deap import base
from deap import creator
from deap import tools
from deap import algorithms

import random
import numpy


from knapsack.knapsack import Knapsack01Problem
from helper.test import readTestFromFile


# Genetic Algorithm constants:
P_CROSSOVER = 0.9  # probability for crossover
P_MUTATION = 0.1   # probability for mutating an individual
MAX_GENERATIONS = 100
HALL_OF_FAME_SIZE = 1


# set the random seed:
RANDOM_SEED = 42
random.seed(RANDOM_SEED)


def deapSolver(items, maxCapacity, testCasePath):
    knapsack = Knapsack01Problem(items, maxCapacity)

    def knapsackValue(individual):
        return knapsack.getValue(individual),  # return a tuple

    toolbox = base.Toolbox()

    # create an operator that randomly returns 0 or 1:
    toolbox.register("zeroOrOne", random.randint, 0, 1)

    # define a single objective, maximizing fitness strategy:
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))

    # create the Individual class based on list:
    creator.create("Individual", list, fitness=creator.FitnessMax)

    # create the individual operator to fill up an Individual instance:
    toolbox.register("individualCreator", tools.initRepeat,
                     creator.Individual, toolbox.zeroOrOne, len(knapsack))

    # create the population operator to generate a list of individuals:
    toolbox.register("populationCreator", tools.initRepeat,
                     list, toolbox.individualCreator)

    # fitness calculation

    toolbox.register("evaluate", knapsackValue)

    # genetic operators:mutFlipBit

    # Tournament selection with tournament size of 3:
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Single-point crossover:
    toolbox.register("mate", tools.cxTwoPoint)

    # Flip-bit mutation:
    # indpb: Independent probability for each attribute to be flipped
    toolbox.register("mutate", tools.mutFlipBit,
                     indpb=1.0/len(knapsack))

    # create initial population (generation 0):
    population = toolbox.populationCreator(n=len(knapsack))

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", numpy.max)
    stats.register("avg", numpy.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print best solution found:
    best = hof.items[0]

    # Write result to file
    with open('result/resultDeap.txt', 'a') as writer:
        total_weight, computed_value = knapsack.result(best)

        writer.write(f'Solution for {testCasePath}\n')
        writer.write(f'Total weight: {total_weight}\n')
        writer.write(f'Total value: {computed_value}\n')
        writer.write(f'Packed items: {None}\n')
        writer.write(f'Packed_weights: {None}\n')
        writer.write(f'Best Ever Individual: {best}\n')
        writer.write(f"Best Ever Fitness = {best.fitness.values[0]}\n")


def solver():
    testCases = ['00Uncorrelated',
                 '01WeaklyCorrelated',
                 '02StronglyCorrelated',
                 '03InverseStronglyCorrelated',
                 '04AlmostStronglyCorrelated',
                 '05SubsetSum',
                 '06UncorrelatedWithSimilarWeights',
                 '07SpannerUncorrelated',
                 '08SpannerWeaklyCorrelated',
                 '09SpannerStronglyCorrelated',
                 '10MultipleStronglyCorrelated',
                 '11ProfitCeiling',
                 '12Circle']

    nTest = ['00050']

    for test in testCases:
        for n in nTest:
            filePath = f"test/{test}/n{n}/R01000/s001.kp"
            _, _, capacities, items = readTestFromFile(filePath)

            deapSolver(items, capacities[0], filePath)


def main():
    solver()


if __name__ == '__main__':
    main()
