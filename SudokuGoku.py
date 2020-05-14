import pandas as pd
import numpy as np
import tabulate as tb
import time

class SudokuSolver:
    """
    Sudoku Solver class

    Parameters:
    sudoku (pandas or numpy array): Sudoku in either pandas or numpy array format

    Returns:
    None
    """

    _debug = False

    _squares = np.array([
        [1, 1, 1, 2, 2, 2, 3, 3, 3],
        [1, 1, 1, 2, 2, 2, 3, 3, 3],
        [1, 1, 1, 2, 2, 2, 3, 3, 3],
        [4, 4, 4, 5, 5, 5, 6, 6, 6],
        [4, 4, 4, 5, 5, 5, 6, 6, 6],
        [4, 4, 4, 5, 5, 5, 6, 6, 6],
        [7, 7, 7, 8, 8, 8, 9, 9, 9],
        [7, 7, 7, 8, 8, 8, 9, 9, 9],
        [7, 7, 7, 8, 8, 8, 9, 9, 9]
    ]
    )

    def __init__(self, sudoku):

        if not isinstance(sudoku, pd.DataFrame) and not isinstance(sudoku, np.ndarray):
            raise ValueError("Sudoku must be either a Pandas or a Numpy Array")

        if isinstance(sudoku, np.ndarray):
            self._sudoku = pd.DataFrame(sudoku)
        else:
            self._sudoku = sudoku

        self._original = self._sudoku.copy()

        if not self.__check_sudoku():
            raise ValueError("Initial sudoku is invalid")

    def draw_sudoku(self, original = False):
        """Draws the sudoku in a grid (original or solution)

        Parameters:
        original (boolean): Indicates whether the sudoku to be printed is the original. Default value is False.

        Returns:
        None

        """

        printable = np.empty([9, 9], dtype="str")

        if original:
            sudoku = self._original
        else:
            sudoku = self._sudoku

        for row in range(0, 9):
            for col in range(0, 9):
                if sudoku.T[row][col] != 0:
                    printable[row][col] = str(sudoku.T[row][col])

        print(tb.tabulate(printable, tablefmt="grid"))

    def __is_correct(self, check_set):
        """INTERNAL: Checks whether the set of 9 elements provided doesn't contain any repeated number

        Parameters:
        check_set (array): Array with 9 numbers from a row, column or square in a Sudoku

        Returns:
        boolean: True if the set is correct, False otherwise

        """

        unique, counts = np.unique(check_set, return_counts=True)

        dict_set = dict(zip(unique, counts))

        for i in dict_set:
            if i != 0:
                if dict_set[i] > 1:
                    return False

        return True

    def __check_sudoku(self):
        """INTERNAL: Check rows, columns and squares

        Parameters:
        None

        Returns:
        boolean: True if the Sudoku is correct, False otherwise

        """

        for i in range(0, 9):

            if not self.__is_correct(self._sudoku[i]) or not self.__is_correct(self._sudoku.T[i]) or not self.__is_correct(np.where(self._squares == (i + 1), self._sudoku, 0)):
                return False

        return True

    def __is_complete(self):
        """INTERNAL: Check rows, columns and squares

        Parameters:
        None

        Returns:
        boolean: True if the Sudoku is correct, False otherwise

        """

        return self._sudoku.to_numpy().sum() == (45 * 9)

    def __next_empty(self):
        """INTERNAL: Gets the next gap in the sudoku to be filled

        Parameters:
        None

        Returns:
        row, col: Row and column in the sudoku to be filled

        """

        for row in range(0, 9):
            for col in range(0, 9):
                if self._sudoku[row][col] == 0:
                    return row, col

        return -1, -1

    def __fill_sudoku_v1(self, n=1):
        """INTERNAL: Solves sudoku recursively checking every value from 1 to 9 for each empty cell

        Parameters:
        n (int): OPTIONAL. Defines the iteration for debug purposes

        Returns:
        boolean: True if the Sudoku is correct, False otherwise

        """

        # If the Sudoku is already solved, return True

        if self.__is_complete():

            if self._debug:
                print(f"Sudoku solved in the iteration {n}!")

            return True

        # Look for the next gap to fill

        row, col = self.__next_empty()

        if self._debug:
            print(f"Iteration {n}: Lets fill the gap ({row}, {col}).")

        for i in range(1, 10):

            # Check the value

            if self._debug:
                print(f"Iteration {n}: Checking the value {i}.")

            self._sudoku[row][col] = i

            if self.__check_sudoku():

                if self._debug:
                    print(f"Iteration {n}: The sudoku seems valid. Move to the next gap.")

                if self.__fill_sudoku_v1(n + 1):
                    return True

        self._sudoku[row][col] = 0

        return False

    def __get_options(self):
        """INTERNAL: Get the different options for each cell in the sudoku based on the existing values in row, column and square where the cell is.

        Parameters:
        None

        Returns:
        array: Possible values for the cell

        """

        options = pd.DataFrame([], index=np.arange(0, 9), columns=np.arange(9))

        for row in range(0, 9):
            for col in range(0, 9):

                if self._sudoku[row][col] != 0:
                    options[row][col] = [self._sudoku[row][col]]
                else:
                    if self._debug:
                        print(f"Analyzing ({row}, {col}) --> {self._sudoku[row][col]}")

                    options_base = list(range(1, 10))

                    # Remove options in col

                    if self._debug:
                        print("\tAnalysis 1: ", self._sudoku.T[col].to_numpy())

                    for value in self._sudoku.T[col]:
                        if value in options_base:
                            options_base.remove(value)

                    # Remove options in row

                    if self._debug:
                        print("\tAnalysis 2: ", self._sudoku[row].to_numpy())

                    for value in self._sudoku[row]:
                        if value in options_base:
                            options_base.remove(value)

                    # Remove options in square

                    if self._debug:
                        print(f"\tBlock is {(int(col / 3) * 3 + (int(row / 3) + 1))}.")
                        print("\tAnalysis square: ", np.unique(np.where(self._squares == int(col / 3) * 3 + (int(row / 3) + 1), self._sudoku, 0)))

                    for value in np.unique(np.where(self._squares == int(col / 3) * 3 + (int(row / 3) + 1), self._sudoku, 0)):
                        if value in options_base:
                            options_base.remove(value)

                    options[row][col] = options_base

        return options

    def __fill_sudoku_v2(self, options, n=1):
        """INTERNAL: Solves sudoku recursively checking only the possible values for each gap according to the position in the grid

        Parameters:
        options (array): Matrix with the options for each cell
        n (int): OPTIONAL. Iteration for debug purposes

        Returns:
        boolean: True if the Sudoku is correct, False otherwise

        """

        # Si el sudoku está completado, lo devuelvo

        if self.__is_complete():

            if self._debug:
                print(f"Sudoky solved in iteration {n}!")

            return True

        # Si no, busco el siguiente elemento vacío y lo empiezo a llenar

        row, col = self.__next_empty()

        if self._debug:
            print(f"Iteration {n}: Lets fill the gap ({row}, {col}). Options are {options[row][col]}")

        for i in options[row][col]:

            # Check the value

            if self._debug:
                print(f"Iteration {n}: Checking value {i}.")

            self._sudoku[row][col] = i

            if self._debug:
                self.draw_sudoku()

            if self.__check_sudoku():

                if self._debug:
                    print(f"Iteration {n}: Sudoku seems valid. Lets fill the next gap.")

                if self.__fill_sudoku_v2(options, n + 1):
                    return True

        if self._debug:
            print(f"Iteration {n}: No options valid. Back to previous iteration.")

        self._sudoku[row][col] = 0

        return False

    def solve_sudoku(self, method):
        """Solves sudoku using the method provided

        Parameters:
        method (str): Method to be used for solving the sudoku. Options are:
            * brute: Check every value from 1 to 9
            * options: Check only possible values for each cell

        Returns:
        boolean: True if the Sudoku is solved, False otherwise

        """

        if method not in ("brute", "options"):
            raise ValueError("Method must be either 'brute' or 'options'")

        print(f"\nSolving sudoku using method '{method}'...\n")

        t_start = time.time()

        if method == "brute":

            if self.__fill_sudoku_v1():

                t_end = time.time()

                if input(f"Sudoku solved in {round(t_end - t_start, 2)} seconds :). Do you want to see the result? (Y/N): ").upper() == "Y":
                    self.draw_sudoku()
            else:

                print("Sudoku couldn't be solved :(\n")

        else:

            if self.__fill_sudoku_v2(self.__get_options()):

                t_end = time.time()

                if input(f"Sudoku solved in {round(t_end - t_start, 2)} seconds :). Do you want to see the result? (Y/N): ").upper() == "Y":
                    self.draw_sudoku()

            else:

                print("Sudoku couldn't be solved :(\n")
