ALL_NUMBERS = set(range(1,10))
BLANK = 0

class SudokuBoard:

    cellValues = []
    rowSets = []
    colSets = []
    blockSets = []

    def __init__(self,make_blank=True):
        if not make_blank:
            return
        for i in range(9):
            self.cellValues.append([BLANK] * 9)
            self.rowSets.append(ALL_NUMBERS.copy())
            self.colSets.append(ALL_NUMBERS.copy())
            self.blockSets.append(ALL_NUMBERS.copy())

    def copy(self):
        cp = SudokuBoard(make_blank=False)
        for y in range(9):
            cp.rowSets[y] = self.rowSets[y].copy()
            cp.colSets[y] = self.colSets[y].copy()
            cp.blockSets[y] = self.blockSets[y].copy()
        cp.cellValues = self.cellValues.copy()
        assert(len(cp.cellValues) == 9)
        assert(len(cp.rowSets) == 9)
        assert(len(cp.colSets) == 9)
        assert(len(cp.blockSets) == 9)
        return cp

    def pretty_print(self):
        for row in self.cellValues:
            for cell in row:
                if cell == BLANK:
                    print('_', end="")
                else:
                    print(cell, end="")
                print(' ', end="")
            print('\n')
        print('\n')

    @staticmethod
    def validate_coords(x,y):
        bad_x = x < 0 or x >= 9
        bad_y = y < 0 or y >= 9
        if bad_x and bad_y:
            raise ValueError("Both x and y coordinates were out of bounds: ({0},{1}".format(x,y))
        elif bad_x:
            raise ValueError("X coordinate was out of range in ({0},{1})".format(x,y))
        elif bad_y:
            raise ValueError("Y coordinate was out of range in ({0},{1})".format(x,y))

    @staticmethod
    def get_block_index(x,y):
        SudokuBoard.validate_coords(x,y)
        return 3 * (y // 3) + x // 3

    def get_legal_values(self, x, y):
        SudokuBoard.validate_coords(x,y)
        if self.cellValues[y][x] != BLANK:
            return set()
        else:
            retSet = ALL_NUMBERS.copy()
            retSet.intersection_update(self.rowSets[y])
            retSet.intersection_update(self.colSets[x])
            retSet.intersection_update(self.blockSets[SudokuBoard.get_block_index(x,y)])
            return retSet

    def update_cell(self, x, y, value):
        SudokuBoard.validate_coords(x,y)
        if value == BLANK:
            raise ValueError("Use clear_cell instead of updating a cell to blank.")
        legal_values = self.get_legal_values(x,y)
        if value not in legal_values:
            raise ValueError("Value: {0} not a legal value for cell ({1},{2})".format(value, x,y))
        block_index = SudokuBoard.get_block_index(x,y)
        self.cellValues[y][x] = value
        self.rowSets[y].difference_update([value])
        self.colSets[x].difference_update([value])
        self.blockSets[block_index].difference_update([value])

    def clear_cell(self,x,y):
        SudokuBoard.validate_coords(x,y)
        value = self.cellValues[y][x]
        if value != BLANK:
            raise ValueError("Attempting to clear an already empty cell: ({0},{1})".format(x,y))
        block_index = SudokuBoard.get_block_index(x,y)
        self.cellValues[y][x] = BLANK
        self.rowSets[y].union_update([value])
        self.colSets[x].union_update([value])
        self.blockSets[block_index].union_update([value])

    def get_most_constrained(self):
        smallest_remaining = 100
        remaining = None
        point = None
        for y in  range(9):
            for x in range(9):
                if self.cellValues[y][x] != BLANK:
                    continue
                legal_values = self.get_legal_values(x,y)
                count = len(legal_values)
                if count == 0:
                    return { 'x' : x, 'y' : y, 'choices' : legal_values }
                elif count < smallest_remaining:
                    point = (x,y)
                    smallest_remaining = count
                    remaining = legal_values
        return { 'x': point[0], 'y': point[1], "choices": remaining}

    def feasible(self):
        most_constrained = self.get_most_constrained()
        return most_constrained['choices'] == set()

    def solved(self):
        for row in self.cellValues:
            for cell in row:
                if cell == BLANK:
                    return False
        return True

def solve_board(board):
    if board.solved():
        print("Board solved!")
        return board
    else:
        next_move = board.get_most_constrained()
        if next_move['choices'] == set():
            print("Infeasible board. Backtracing.")
            return None
        else:
            for choice in next_move['choices']:
                next = board.copy()
                next.update_cell(next_move['x'], next_move['y'], choice)
                solution = solve_board(next)
                if solution:
                    return solution

if __name__ == "__main__":
    board = SudokuBoard()
    board.pretty_print()
    solution = solve_board(board)
    solution.pretty_print()