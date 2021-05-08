from ortools.algorithms import pywrapknapsack_solver
import os
from helper.test import readTestFromFile


def ortoolsSolver(values, weights, capacities, testCasePath):
    # Create the solver.
    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.
        KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

    solver.Init(values, weights, capacities)

    # Set computation budget for 30 seconds
    solver.set_time_limit(30)

    computed_value = solver.Solve()

    packed_items = []
    packed_weights = []
    individuals = []
    total_weight = 0
    print('Total value =', computed_value)

    for i in range(len(values)):
        if solver.BestSolutionContains(i):
            individuals.append(1)
            packed_items.append(i)
            packed_weights.append(weights[0][i])
            total_weight += weights[0][i]
        else:
            individuals.append(0)

    print('Total weight:', total_weight)
    print('Packed items:', packed_items)
    print('Packed_weights:', packed_weights)

    # Write result to file
    with open('result/resultORTools.txt', 'a') as writer:
        writer.write(f'Solution for {testCasePath}\n')
        writer.write(f'Total weight: {total_weight}\n')
        writer.write(f'Total value: {computed_value}\n')
        writer.write(f'Packed items: {packed_items}\n')
        writer.write(f'Packed_weights: {packed_weights}\n')
        writer.write(f'Best Ever Individual: {individuals}\n')
        writer.write(f"Best Ever Fitness = {None}\n")


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
            values, weights, capacities, _ = readTestFromFile(filePath)

            ortoolsSolver(values, weights, capacities, filePath)


def main():
    solver()


if __name__ == '__main__':
    main()
