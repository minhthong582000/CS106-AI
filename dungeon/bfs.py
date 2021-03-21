import collections

queue = collections.deque([])
actionQueue = collections.deque([])
visited = set()


def getAction(index):
    switcher = {
        0: "u",  # Up
        1: "d",  # Down
        2: "r",  # Right
        3: "l"   # Left
    }

    return switcher.get(index)


def exploreNeighbor(node):
    dr = [-1, 1, 0, 0]
    dc = [0, 0, 1, -1]

    legalState = []

    for i in range(0, 4):
        rr = node[0] + dr[i]
        cc = node[1] + dc[i]

        if rr < 0 or cc < 0:
            continue

        if rr >= R or cc >= C:
            continue

        if map[rr][cc] == "#":
            continue

        if (rr, cc) in visited:
            continue

        newPos = (rr, cc)
        newAction = getAction(i)

        newState = (newPos, newAction)
        legalState.append(newState)

    return legalState


def dungeonSolver(map, R, C, start, end):
    tmp = []

    queue.append([start])
    actionQueue.append([0])

    visited.add(start)

    while queue:
        node = queue.popleft()
        action = actionQueue.popleft()

        if node[-1] == end:
            tmp += action[1:]
            break

        for state in exploreNeighbor(node[-1]):
            visited.add(state[0])
            actionQueue.append(action + [state[1]])
            queue.append(node + [state[0]])

    return tmp


R = 5
C = 7
map = [[".", ".", ".", "#", ".", ".", "."],
       [".", "#", ".", ".", ".", "#", "."],
       [".", "#", ".", ".", ".", ".", "."],
       [".", ".", "#", "#", ".", ".", "."],
       ["#", ".", "#", ".", ".", "#", "."]]

start = (0, 0)
end = (4, 3)
result = dungeonSolver(map, R, C, start, end, )
print(f'result: {result}')
