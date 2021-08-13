ALL_NUMBERS = set(range(1,10))
BLANK = 0
BLANK_CHAR = '_'

class SudokuBoard:

    def __init__(self,make_blank=True):
        self.cellValues = []
        self.rowSets = []
        self.colSets = []
        self.blockSets = []
        if make_blank:
            for i in range(9):
                self.cellValues.append([BLANK] * 9)
                self.rowSets.append(ALL_NUMBERS.copy())
                self.colSets.append(ALL_NUMBERS.copy())
                self.blockSets.append(ALL_NUMBERS.copy())

    def copy(self):
        cp = SudokuBoard(make_blank=False)
        for y in range(9):
            cp.rowSets.append(self.rowSets[y].copy())
            cp.colSets.append(self.colSets[y].copy())
            cp.blockSets.append(self.blockSets[y].copy())
        cp.cellValues = self.cellValues.copy()
        assert(len(cp.cellValues) == 9)
        assert(len(cp.rowSets) == 9)
        assert(len(cp.colSets) == 9)
        assert(len(cp.blockSets) == 9)
        return cp

    def to_string(self):
        ret = ""
        for row in self.cellValues:
            for cell in row:
                if cell == BLANK:
                    ret += BLANK_CHAR
                else:
                    ret += str(cell)
                ret += ' '
            ret += '\n'
        return ret

    def pretty_print(self):
        print(self.to_string())

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

    @staticmethod
    def from_string(string_of_board):
        retBoard = SudokuBoard()
        x = 0
        y = 0
        for row in string_of_board.split('\n'):
            for cell in row.split(' '):
                if cell == BLANK_CHAR or cell == '':
                    continue
                else:
                    value = int(cell)
                    retBoard.update_cell(x,y,value)
                x += 1
            y += 1
            x = 0
        return retBoard

    @staticmethod
    def from_file(path):
        with open(path, 'r') as pipe:
            string = pipe.read()
            return SudokuBoard.from_string(string)

    def to_file(self, path):
        output_string = self.to_string()
        with open(path, 'w') as pipe:
            pipe.write(output_string)

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

def variable_number(x, y, value):
    """
    Returns the minisat variable number meaning 'The Cell (x,y) contains value'
    """
    SudokuBoard.validate_coords(x,y)
    # +1 because 0 doesn't negate well
    return y * 81 + x * 9 + (value - 1) + 1

def assignment_of_number(variable_index):
    variable_index = variable_index - 1
    y = variable_index // 81
    x = (variable_index - 81 * y) // 9
    value = (variable_index - 81 * y - x * 9) + 1
    SudokuBoard.validate_coords(x,y)
    assert(value >= 1)
    assert(value <= 9)
    return { 'x' : x, 'y' : y, 'value' : value}

def every_cell_has_some_value(x,y):
    clause = []
    for value in ALL_NUMBERS:
        clause.append(variable_number(x,y,value))
    return [clause]

def every_cell_has_one_number(x,y):
    clauses = []
    for value_a in range(1,9):
        for value_b in range(value_a + 1, 10):
            variable_i = -1 * variable_number(x,y,value_a)
            varibale_j = -1 * variable_number(x,y,value_b)
            clause = [ variable_i, varibale_j]
            clauses.append(clause)
    return clauses

def every_column_contains_every_number(x):
    clauses = []
    for value in ALL_NUMBERS:
        clause = [] # Either 0,1 = 1 or 0,2 = 1 or 0,3 = 1...
        for row in range(9):
            clause.append(variable_number(x, row, value))
        clauses.append(clause)
    return clauses

def every_row_contains_every_number(y):
    clauses = []
    for value in ALL_NUMBERS:
        clause = [] # Either 1,0 = 1 or 2,0 = 1 or 3,0 = 1...
        for col in range(9):
            clause.append(variable_number(col, y, value))
        clauses.append(clause)
    return clauses

def every_block_contains_every_number(index):
    x_min = (index % 3) * 3
    y_min = index // 3 * 3
    clauses = []
    for value in ALL_NUMBERS:
        clause = []
        for x in range(x_min, x_min + 3):
            for y in range(y_min, y_min + 3):
                clause.append(variable_number(x,y,value))
        clauses.append(clause)
    return clauses

def base_board_formulation():
    clauses = []
    for x in range(9):
        clauses += every_column_contains_every_number(x)
        clauses += every_row_contains_every_number(x)
        clauses += every_block_contains_every_number(x)
        for y in range(9):
            clauses += every_cell_has_some_value(x,y)
            clauses += every_cell_has_one_number(x,y)
    return clauses

def initial_problem_constraints(board):
    clauses = []
    for x in range(9):
        for y in range(9):
            value = board.cellValues[y][x]
            if value != BLANK:
                variable = variable_number(x,y, value)
                clauses.append([variable])
    return clauses

def emit_problem(board, path):
    num_variables = 9 * 9 * 9
    base_clauses = base_board_formulation()
    problem_specific_clauses = initial_problem_constraints(board)
    num_clauses = len(base_clauses) + len(problem_specific_clauses)
    with open(path, 'w') as pipe:
        pipe.write('p cnf {0} {1}\n'.format(num_variables, num_clauses))
        for clause in problem_specific_clauses + base_clauses:
            for element in clause:
                pipe.write(str(element) + ' ')
            pipe.write('\n')

if __name__ == "__main__":
    board = SudokuBoard()
    board.pretty_print()
    solution = solve_board(board)
    solution.pretty_print()
    emit_problem(SudokuBoard(), "test.cnf")