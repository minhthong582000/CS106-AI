import sys
import collections
import numpy as np
import heapq
import time
import numpy as np
global posWalls, posGoals


class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""

    def __init__(self):
        self.Heap = []
        self.Count = 0
        self.len = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0


"""Load puzzles and define the rules of sokoban"""


def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n', '') for x in layout]
    layout = [','.join(layout[i]) for i in range(len(layout))]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == ' ':
                layout[irow][icol] = 0   # free space
            elif layout[irow][icol] == '#':
                layout[irow][icol] = 1  # wall
            elif layout[irow][icol] == '&':
                layout[irow][icol] = 2  # player
            elif layout[irow][icol] == 'B':
                layout[irow][icol] = 3  # box
            elif layout[irow][icol] == '.':
                layout[irow][icol] = 4  # goal
            elif layout[irow][icol] == 'X':
                layout[irow][icol] = 5  # box on goal
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)])

    # print(layout)
    return np.array(layout)


def transferToGameState2(layout, player_pos):
    """Transfer the layout of initial puzzle"""
    maxColsNum = max([len(x) for x in layout])
    temp = np.ones((len(layout), maxColsNum))
    for i, row in enumerate(layout):
        for j, val in enumerate(row):
            temp[i][j] = layout[i][j]

    temp[player_pos[1]][player_pos[0]] = 2
    return temp


def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0])  # e.g. (2, 2)


def PosOfBoxes(gameState):
    """Return the positions of boxes"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5)))  # e.g. ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5))


def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1))  # e.g. like those above


def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5)))  # e.g. like those above


def isEndState(posBox):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(posBox) == sorted(posGoals)


def isLegalAction(action, posPlayer, posBox):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper():  # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in posBox + posWalls


def legalActions(posPlayer, posBox):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1, 0, 'u', 'U'], [1, 0, 'd', 'D'],
                  [0, -1, 'l', 'L'], [0, 1, 'r', 'R']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in posBox:  # the move was a push
            action.pop(2)  # drop the little letter
        else:
            action.pop(3)  # drop the upper letter
        if isLegalAction(action, posPlayer, posBox):
            legalActions.append(action)
        else:
            continue
    # e.g. ((0, -1, 'l'), (0, 1, 'R'))
    return tuple(tuple(x) for x in legalActions)


def updateState(posPlayer, posBox, action):
    """Return updated game state after an action is taken"""
    xPlayer, yPlayer = posPlayer  # the previous position of player
    newPosPlayer = [xPlayer + action[0], yPlayer +
                    action[1]]  # the current position of player
    posBox = [list(x) for x in posBox]
    if action[-1].isupper():  # if pushing, update the position of box
        posBox.remove(newPosPlayer)
        posBox.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1]])
    posBox = tuple(tuple(x) for x in posBox)
    newPosPlayer = tuple(newPosPlayer)
    return newPosPlayer, posBox


def isFailed(posBox):
    """This function used to observe if the state is potentially failed, then prune the search"""
    rotatePattern = [[0, 1, 2, 3, 4, 5, 6, 7, 8],
                     [2, 5, 8, 1, 4, 7, 0, 3, 6],
                     [0, 1, 2, 3, 4, 5, 6, 7, 8][::-1],
                     [2, 5, 8, 1, 4, 7, 0, 3, 6][::-1]]
    flipPattern = [[2, 1, 0, 5, 4, 3, 8, 7, 6],
                   [0, 3, 6, 1, 4, 7, 2, 5, 8],
                   [2, 1, 0, 5, 4, 3, 8, 7, 6][::-1],
                   [0, 3, 6, 1, 4, 7, 2, 5, 8][::-1]]
    allPattern = rotatePattern + flipPattern

    for box in posBox:
        if box not in posGoals:
            board = [(box[0] - 1, box[1] - 1), (box[0] - 1, box[1]), (box[0] - 1, box[1] + 1),
                     (box[0], box[1] - 1), (box[0],
                                            box[1]), (box[0], box[1] + 1),
                     (box[0] + 1, box[1] - 1), (box[0] + 1, box[1]), (box[0] + 1, box[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posWalls:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posWalls and newBoard[5] in posBox:
                    return True
                elif newBoard[1] in posBox and newBoard[2] in posBox and newBoard[5] in posBox:
                    return True
                elif newBoard[1] in posBox and newBoard[6] in posBox and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls:
                    return True
    return False


"""Implement all approcahes"""


def depthFirstSearch(gameState):
    """Implement depthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)  # Vi tri hien tai cua cac Boxes
    beginPlayer = PosOfPlayer(gameState)  # Vi tri hien tai cua Player

    startState = (beginPlayer, beginBox)

    frontier = collections.deque([[startState]])

    exploredSet = set()
    actions = [[0]]
    temp = []

    while frontier:
        node = frontier.pop()
        node_action = actions.pop()

        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break

        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)
                if isFailed(newPosBox):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])

    return temp


def breadthFirstSearch(gameState):
    """
    Implement breadthFirstSearch approach
    Sử dụng thuật toán BFS để tìm lời giải - Sử dụng CTDL queue để lưu các state và action tương ứng

    gameState - state hiện tại của game (bản đồ)

    return - 1 list các actions để đến được goal, nếu không đến được trả về "[]"
    """

    # Lấy ra các vị trí bắt đầu của Boxes
    # e.g. ((0,0), (2,3))
    beginBox = PosOfBoxes(gameState)

    # Lấy ra vị trí bắt đầu của player
    # e.g. (1,0)
    beginPlayer = PosOfPlayer(gameState)

    # startState là tuple dùng để lưu state khởi đầu
    # Bao gồm vị trí bắt đầu của player và boxes
    # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    startState = (beginPlayer, beginBox)

    # frontier là 1 queue dùng để store states
    # Lưu các list - trong đó mỗi list sẽ đại diện cho 1 tập các states
    # đã được explore từ vị trí khởi đầu
    #
    # Bắt đầu bằng startState - state khởi đầu
    frontier = collections.deque([[startState]])

    # actions là 1 queue dùng để store actions
    # Lưu các list - trong đó mỗi list sẽ đại diện cho 1 tập các actions cần làm để
    # đạt được state tương ứng ở frontier
    #
    # Bắt đầu bằng [0] - không có hành động
    actions = collections.deque([[0]])

    # Store các state đã được explore
    exploredSet = set()

    # list lưu các actions để đến được goal (Kết thúc game)
    temp = []

    # Implement breadthFirstSearch here
    # Ta sẽ liên tục lấy ra các phần tử ở đầu frontier cho tới khi frontier rỗng
    while frontier:
        # Lấy ra list ở đầu frontier queue lưu tập các states
        node = frontier.popleft()

        # Lấy ra list ở đầu action queue lưu tập các actions
        node_action = actions.popleft()

        # Lấy ra vị trí các boxes ở cuối node list (state gần nhất mà ta đã thêm vào frontier)
        # Nếu vị trí các boxes đã ở đúng vị trí (endState)
        # lưu lại list các actions tương ứng với states vào temp, kết thúc vòng lặp
        if isEndState(node[-1][-1]):
            # Lưu actions vào temp, bỏ qua phần tử 0 lúc khởi tạo
            temp += node_action[1:]
            break

        # Nếu các boxes vẫn chưa tới được đúng vị trí
        # Ta kiểm tra xem state mới nhất ở cuối node list đã đuợc explore chưa
        if node[-1] not in exploredSet:
            # Nếu chưa ta thêm state đó vào exploreSet
            exploredSet.add(node[-1])

            # Sau đó, tìm kiếm các action mà ta có thể thực hiện dựa trên
            # vị trí hiện tại của player, boxes (Lấy từ state đó)
            for action in legalActions(node[-1][0], node[-1][1]):

                # Lấy ra vị ví mới của các boxes và player từ action (u, d, r, l, U, D, R, L)
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)

                # Nếu các box bị kẹt, chuyển sang action khác
                if isFailed(newPosBox):
                    continue

                # action không làm các boxes bị kẹt
                # Ta sẽ được một state mới
                # Thêm tập các states cũ cùng với state mới vào frontier
                frontier.append(node + [(newPosPlayer, newPosBox)])
                # Thêm tập các actions cũ cùng với action mới vào frontier
                actions.append(node_action + [action[-1]])

    # Trả về list các hành động để đến được goal !!
    return temp


def cost(actions):
    """
    A cost function
    Sử dụng kết hợp với UCS
    Dùng để tính toán chi phí cho các actions
    Với mỗi lần di chuyển player ta sẽ tính là 1 cost,
    không bao gồm các hành động di chuyển các boxes
    """

    # Đếm sô lượng action được kí hiệu viết thường (lowercase)
    # hay action làm di chuyển player
    return len([x for x in actions if x.islower()])


def uniformCostSearch(gameState):
    """
    Implement uniformCostSearch approach
    Sử dụng thuật toán UCS để tìm lời giải

    Kèm theo CTDL priority queue để lưu các state và action tương ứng,
    trong đó nhờ sự giúp đỡ của trọng số priority (ưu tiên đường đi có trọng số nhỏ nhất
     - hay đường đi với số bước đi ít nhất)
    ta sẽ tìm được đường đi tối ưu để đến được goal

    gameState - state hiện tại của game (bản đồ)

    return - 1 list các actions để đến được goal, nếu không đến được trả về "[]"
    """

    # Lấy ra các vị trí bắt đầu của Boxes
    # e.g. ((0,0), (2,3))
    beginBox = PosOfBoxes(gameState)

    # Lấy ra vị trí bắt đầu của player
    # e.g. (1,0)
    beginPlayer = PosOfPlayer(gameState)

    # startState là tuple dùng để lưu state khởi đầu
    # Bao gồm vị trí bắt đầu của player và boxes
    # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    startState = (beginPlayer, beginBox)

    # frontier là 1 queue dùng để store states
    # Lưu các list - trong đó mỗi list sẽ đại diện cho 1 tập các states
    # đã được explore từ vị trí khởi đầu
    #
    # Bắt đầu bằng startState - state khởi đầu, với trọng số bằng 0
    frontier = PriorityQueue()
    frontier.push([startState], 0)

    # Store các state đã được explore
    exploredSet = set()

    # actions là 1 queue dùng để store actions
    # Lưu các list - trong đó mỗi list sẽ đại diện cho 1 tập các actions cần làm để
    # đạt được state tương ứng ở frontier
    #
    # Bắt đầu bằng [0] - không có hành động, với trọng số bằng 0
    actions = PriorityQueue()
    actions.push([0], 0)

    # list lưu các actions để đến được goal (Kết thúc game)
    temp = []

    # Implement uniform cost search here
    # Ta sẽ liên tục lấy ra các phần tử ở đầu frontier cho tới khi frontier rỗng
    while frontier.isEmpty() == False:
        # Lấy ra list ở đầu frontier queue có trọng số nhỏ nhất,
        # lưu tập các states
        node = frontier.pop()

        # Lấy ra list ở đầu action queue có trọng số nhỏ nhất,
        # lưu tập các actions
        node_action = actions.pop()

        # Lấy ra vị trí các boxes ở cuối node list (state gần nhất mà ta đã thêm vào frontier)
        # Nếu vị trí các boxes đã ở đúng vị trí (endState)
        # lưu lại list các actions tương ứng với states vào temp, kết thúc vòng lặp
        if isEndState(node[-1][-1]):
            # Lưu actions vào temp, bỏ qua phần tử 0 lúc khởi tạo
            temp += node_action[1:]
            break

        # Nếu các boxes vẫn chưa tới được đúng vị trí
        # Ta kiểm tra xem state mới nhất ở cuối node list đã đuợc explore chưa
        if node[-1] not in exploredSet:
            # Nếu chưa ta thêm state đó vào exploreSet
            exploredSet.add(node[-1])

            # Sau đó, tìm kiếm các action mà ta có thể thực hiện dựa trên
            # vị trí hiện tại của player, boxes (Lấy từ state đó)
            for action in legalActions(node[-1][0], node[-1][1]):

                # Lấy ra vị ví mới của các boxes và player từ action (u, d, r, l, U, D, R, L)
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)

                # Nếu các box bị kẹt, chuyển sang action khác
                if isFailed(newPosBox):
                    continue

                # Tính toán trọng số ưu tiên (hay cost) của chuỗi actions
                # Bao gồm cả action mà ta vừa thêm vào
                currentCost = cost((node_action + [action[-1]])[1:])

                # action không làm các boxes bị kẹt
                # Ta sẽ được một state mới
                # Thêm tập các states cũ cùng với state mới vào frontier
                # Kèm theo đó là trọng số
                frontier.push(
                    node + [(newPosPlayer, newPosBox)], currentCost)
                # Thêm tập các actions cũ cùng với action mới vào frontier
                # Kèm theo đó là trọng số
                actions.push(node_action + [action[-1]], currentCost)

    # Trả về list các hành động để đến được goal !!
    return temp


def manhattan(box, goal):
    return abs(box[0] - goal[0]) + abs(box[1] - goal[1])


def heuristicCost(posBox):
    boxesCopy = list(posBox)

    hCost = 0

    for goal in posGoals:
        b, h = min([(b, manhattan(b, goal))
                    for b in boxesCopy], key=lambda t: t[1])
        hCost += h
        boxesCopy.remove(b)

    return hCost


def AStarSearch(gameState):

    beginBox = PosOfBoxes(gameState)

    beginPlayer = PosOfPlayer(gameState)

    startState = (beginPlayer, beginBox)

    frontier = PriorityQueue()
    frontier.push([startState], 0)

    exploredSet = set()

    actions = PriorityQueue()
    actions.push([0], 0)

    temp = []

    # Depth
    depth = 0
    nodeLeft = 1

    while frontier.isEmpty() == False:
        node = frontier.pop()

        node_action = actions.pop()

        nodeLeft -= 1

        if nodeLeft == 0:
            depth += 1

        if isEndState(node[-1][-1]):
            temp += node_action[1:]
            break

        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])

            for action in legalActions(node[-1][0], node[-1][1]):
                newPosPlayer, newPosBox = updateState(
                    node[-1][0], node[-1][1], action)

                if isFailed(newPosBox):
                    continue

                currentCost = heuristicCost(node[-1][-1]) + depth

                frontier.push(
                    node + [(newPosPlayer, newPosBox)], currentCost)
                actions.push(node_action + [action[-1]], currentCost)
                nodeLeft += 1

    return temp


"""Read command"""


def readCommand(argv):
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels',
                      help='level of game to play', default='level1.txt')
    parser.add_option('-m', '--method', dest='agentMethod',
                      help='research method', default='bfs')
    args = dict()
    options, _ = parser.parse_args(argv)
    with open('assets/levels/' + options.sokobanLevels, "r") as f:
        layout = f.readlines()
    args['layout'] = layout
    args['method'] = options.agentMethod
    return args


def get_move(layout, player_pos, method):
    time_start = time.time()
    global posWalls, posGoals
    # layout, method = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState2(layout, player_pos)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)
    if method == 'dfs':
        result = depthFirstSearch(gameState)
    elif method == 'bfs':
        result = breadthFirstSearch(gameState)
    elif method == 'ucs':
        result = uniformCostSearch(gameState)
    elif method == 'astar':
        result = AStarSearch(gameState)
    else:
        raise ValueError('Invalid method.')
    time_end = time.time()
    print('Runtime of %s: %.2f second.' % (method, time_end-time_start))
    print(result)
    return result
