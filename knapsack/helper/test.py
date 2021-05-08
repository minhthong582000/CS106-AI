def readTestFromFile(filePath):
    values = []
    weights = [[]]
    capacities = []
    items = []

    with open(filePath, 'r') as reader:
        lines = reader.readlines()

        # Line 2 always contain capacity
        c = int(lines[2].rstrip())
        capacities.append(c)

        # Our weights and values start from line 4
        for line in lines[4:]:
            l = line.rstrip().split(" ")

            values.append(int(l[0]))
            weights[0].append(int(l[1]))
            items.append([int(l[1]), int(l[0])])

    return values, weights, capacities, items


def main():
    values, weights, capacities, items = readTestFromFile(
        "test/02StronglyCorrelated/n01000/R01000/s001.kp")

    print(weights)


if __name__ == '__main__':
    main()
