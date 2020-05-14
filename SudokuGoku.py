import pandas as pd
import numpy as np
import tabulate as tb
import time

class SudokuSolver:

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
            raise ValueError("The sudoku must be either a Pandas or a Numpy Array")

        if isinstance(sudoku, np.ndarray):
            self._sudoku = pd.DataFrame(sudoku)
        else:
            self._sudoku = sudoku

        self._initial_sudoku = self._sudoku.copy()

        if not self.__check_sudoku():
            raise ValueError("Initial sudoku is invalid")

    def draw_sudoku(self):
        '''INFO: Draws the sudoku'''

        printable = np.empty([9, 9], dtype="str")

        for row in range(0, 9):
            for col in range(0, 9):
                if self._sudoku.T[row][col] != 0:
                    printable[row][col] = str(self._sudoku.T[row][col])

        print(tb.tabulate(printable, tablefmt="grid"))

    def __is_correct(self, check_set):
        # Checks whether the set of 9 elements doesn't contain any repeated number

        unique, counts = np.unique(check_set, return_counts=True)

        dict_set = dict(zip(unique, counts))

        for i in dict_set:
            if i != 0:
                if dict_set[i] > 1:
                    return False

        return True

    def __check_sudoku(self):
        # Check rows, columns and squares

        for i in range(0, 9):

            if not self.__is_correct(self._sudoku[i]) or not self.__is_correct(self._sudoku.T[i]) or not self.__is_correct(np.where(self._squares == (i + 1), self._sudoku, 0)):
                return False

        return True

    def __is_complete(self):
        return self._sudoku.to_numpy().sum() == (45 * 9)

    def __next_empty(self):

        for row in range(0, 9):
            for col in range(0, 9):
                if self._sudoku[row][col] == 0:
                    return row, col

        return -1, -1

    def __fill_sudoku_v1(self, n=1):

        # Si el sudoku está completado, lo devuelvo

        if self.__is_complete():

            if self._debug:
                print(f"¡El sudoku está terminado en la iteración {n}!")

            return True

        # Si no, busco el siguiente elemento vacío y lo empiezo a llenar

        row, col = self.__next_empty()

        if self._debug:
            print(f"Iteración {n}: Vamos a por el hueco de ({row}, {col}).")

        for i in range(1, 10):

            # Probamos el valor

            if self._debug:
                print(f"Iteración {n}: Probamos con el valor {i} y comprobamos.")

            self._sudoku[row][col] = i

            if self.__check_sudoku():

                if self._debug:
                    print(f"Iteración {n}: El sudoku parece válido. Pasamos a buscar el siguiente valor")

                if self.__fill_sudoku_v1(n + 1):
                    return True

        self._sudoku[row][col] = 0

        return False

    def __get_options(self):

        options = pd.DataFrame([], index=np.arange(0, 9), columns=np.arange(9))

        for row in range(0, 9):
            for col in range(0, 9):

                if self._sudoku[row][col] != 0:
                    options[row][col] = [self._sudoku[row][col]]
                else:
                    if self._debug:
                        print(f"Analizando ({row}, {col}) --> {self._sudoku[row][col]}")

                    options_base = list(range(1, 10))

                    # Remove options in col

                    if self._debug:
                        print("\tAnálisis 1: ", self._sudoku.T[col].to_numpy())

                    for value in self._sudoku.T[col]:
                        if value in options_base:
                            options_base.remove(value)

                            # Remove options in row

                    if self._debug:
                        print("\tAnálisis 2: ", self._sudoku[row].to_numpy())

                    for value in self._sudoku[row]:
                        if value in options_base:
                            options_base.remove(value)

                    # Remove options in square

                    if self._debug:
                        print(f"\tEl bloque es el {(int(col / 3) * 3 + (int(row / 3) + 1))}.")
                        print("\tAnálisis cuadro: ",
                              np.unique(np.where(self._squares == int(col / 3) * 3 + (int(row / 3) + 1), self._sudoku, 0)))

                    for value in np.unique(np.where(self._squares == int(col / 3) * 3 + (int(row / 3) + 1), self._sudoku, 0)):
                        if value in options_base:
                            options_base.remove(value)

                    options[row][col] = options_base

        return options

    def __fill_sudoku_v2(self, options, n=1):

        # Si el sudoku está completado, lo devuelvo

        if self.__is_complete():

            if self._debug:
                print(f"¡El sudoku está terminado en la iteración {n}!")

            return True

        # Si no, busco el siguiente elemento vacío y lo empiezo a llenar

        row, col = self.__next_empty()

        if self._debug:
            print(f"Iteración {n}: Vamos a por el hueco de ({row}, {col}). Las opciones son {options[row][col]}")

        for i in options[row][col]:

            # Probamos el valor

            if self._debug:
                print(f"Iteración {n}: Probamos con el valor {i} y comprobamos.")

            self._sudoku[row][col] = i

            if self._debug:
                self.draw_sudoku()

            if self.__check_sudoku():

                if self._debug:
                    print(f"Iteración {n}: El sudoku parece válido. Pasamos a buscar el siguiente valor")

                if self.__fill_sudoku_v2(options, n + 1):
                    return True

        if self._debug:
            print(f"Iteración {n}: Ninguna opción es válida. Volvemos a la iteración anterior")

        self._sudoku[row][col] = 0

        return False

    def solve_sudoku(self, method):

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
