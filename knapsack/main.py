from knapsack_Deap import deapSolver
from knapsack_ORTools import ortoolsSolver
from helper.test import readTestFromFile


def solver(solverType):
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

    nTest = ['00050', '00100', '00200', '00500', '01000']

    for test in testCases:
        for n in nTest:
            filePath = f"test/{test}/n{n}/R01000/s001.kp"

            if solverType == "deap":
                _, _, capacities, items = readTestFromFile(filePath)

                deapSolver(items, capacities[0], filePath)

            if solverType == "ortools":
                values, weights, capacities, _ = readTestFromFile(filePath)

                ortoolsSolver(values, weights, capacities, filePath)


def main():
    opt = int(input(":: Welcome to knapsackSolver ::\n"
                    "1.\tortools solver\n2.\tdeap solver\nElse.\tExit\n"))
    if (opt == 1):
        solver("ortools")
    elif (opt == 2):
        solver("deap")
    else:
        print("Bye!")


if __name__ == '__main__':
    main()
