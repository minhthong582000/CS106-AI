import csv


def resToCSV(filePath, csvPath):
    rows = []

    with open(filePath) as reader:
        lines = reader.readlines()
        linesL = len(lines)

        for i in range(0, linesL, 7):
            l = lines[i].split("/")
            group = l[1]
            n = int(l[2].replace("n", ""))
            weight = int(lines[i+1].split(" ")[2].rstrip())
            value = int(lines[i+2].split(" ")[2].rstrip())

            rows.append([group, n, weight, value])

    with open(csvPath, mode='w', newline='', encoding='utf-8') as csvf:
        csv_writer = csv.writer(csvf, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['group', 'n', 'weight', 'value'])
        for row in rows:
            csv_writer.writerow(row)


def main():
    resToCSV("result/resultORTools.txt", "result/resultORTools.csv")
    resToCSV("result/resultDeap.txt", "result/resultDeap.csv")


if __name__ == '__main__':
    main()
