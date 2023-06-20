#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>

#define N 9

namespace py = pybind11;
using namespace std;

class SudokuSolver {
public:
    static bool solveSudoku(vector<vector<int>>& grid) {
        int row, col;
        if (!findEmptyPlace(grid, row, col)) {
            return true;
        }
        for (int num = 1; num <= 9; num++) {
            if (isValidPlace(grid, row, col, num)) {
                grid[row][col] = num;
                if (solveSudoku(grid))
                    return true;
                grid[row][col] = 0;
            }
        }
        return false;
    }

    static py::list solve(py::list grid_list) {
        vector<vector<int>> grid = convertToList(grid_list);
        
        if (solveSudoku(grid)) {
            return createResultList(grid);
        } else {
            throw runtime_error("No solution exists");
        }
    }

    static vector<vector<int>> readMatrixFromFile(const string& filepath) {
        ifstream file(filepath);
        vector<vector<int>> matrix;

        if (file.is_open()) {
            string line;
            while (getline(file, line)) {
                vector<int> row;
                stringstream ss(line);
                string value;

                while (getline(ss, value, ',')) {
                    value.erase(remove_if(value.begin(), value.end(), ::isspace), value.end());
                    if (!value.empty()) {
                        row.push_back(stoi(value));
                    }
                }

                matrix.push_back(row);
            }

            file.close();
        } else {
            throw runtime_error("Unable to open file: " + filepath);
        }

        return matrix;
    }

private:
    static py::list createResultList(const vector<vector<int>>& grid) {
        py::list result;
        for (const auto& row : grid) {
            py::list pyRow;
            for (int num : row) {
                pyRow.append(num);
            }
            result.append(pyRow);
        }
        return result;
    }

    static bool isPresentInCol(const vector<vector<int>>& grid, int col, int num) {
        for (int row = 0; row < N; row++) {
            if (grid[row][col] == num) {
                return true;
            }
        }
        return false;
    }

    static bool isPresentInRow(const vector<vector<int>>& grid, int row, int num) {
        for (int col = 0; col < N; col++) {
            if (grid[row][col] == num) {
                return true;
            }
        }
        return false;
    }

    static bool isPresentInBox(const vector<vector<int>>& grid, int boxStartRow, int boxStartCol, int num) {
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                if (grid[row + boxStartRow][col + boxStartCol] == num) {
                    return true;
                }
            }
        }
        return false;
    }

    static bool findEmptyPlace(const vector<vector<int>>& grid, int& row, int& col) {
        for (row = 0; row < N; row++) {
            for (col = 0; col < N; col++) {
                if (grid[row][col] == 0) {
                    return true;
                }
            }
        }
        return false;
    }

    static bool isValidPlace(const vector<vector<int>>& grid, int row, int col, int num) {
        return !isPresentInRow(grid, row, num) && !isPresentInCol(grid, col, num) && !isPresentInBox(grid, row - row % 3, col - col % 3, num);
    }

    static vector<vector<int>> convertToList(py::list grid_list) {
        vector<vector<int>> grid;
        for (const auto& row : grid_list) {
            vector<int> grid_row;
            for (const auto& num : row) {
                grid_row.push_back(py::cast<int>(num));
            }
            grid.push_back(grid_row);
        }
        return grid;
    }
};

PYBIND11_MODULE(sudoku, m) {
    m.def("read_file", &SudokuSolver::readMatrixFromFile, "Зчитує матрицю з файлу");
    m.def("solve", &SudokuSolver::solve, "Вирішує судоку");
    m.def("is_valid_sudoku", &SudokuSolver::solveSudoku, "Виконує валідацію поля для судоку");
}