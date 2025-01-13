from ortools.linear_solver import pywraplp
solver = pywraplp.Solver.CreateSolver('GLOP')
x = solver.NumVar(0, solver.infinity(), 'x')
solver.Add()
solver.Maximize()
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(solver.Objective().Value())
    print(x.solution_value())


from ortools.sat.python import cp_model

# Lớp dùng để in các nghiệm tạm thời
class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s = %i' % (v.Name(), self.Value(v)), end=' ')
        print()

    def solution_count(self):
        return self.__solution_count

model = cp_model.CpModel()

x = {}
for i in range(5):
    x[i] = model.NewIntVar(1, 5, 'x[' + str(i) + ']')

# Thêm ràng buộc
model.Add(x[2] + 3 != x[1])  # x[2] + 3 ≠ x[1]
model.Add(x[3] <= x[4])      # x[3] ≤ x[4]
model.Add(x[2] + x[3] == x[0] + 1)  # x[2] + x[3] = x[0] + 1
model.Add(x[4] <= 3)         # x[4] ≤ 3
model.Add(x[1] + x[4] == 7)  # x[1] + x[4] = 7

# If-Then-Else: Nếu x[2] == 1 thì x[4] ≠ 2
b = model.NewBoolVar('b')
model.Add(x[2] == 1).OnlyEnforceIf(b)  # b = True khi x[2] == 1
model.Add(x[2] != 1).OnlyEnforceIf(b.Not())  # b = False khi x[2] ≠ 1
model.Add(x[4] != 2).OnlyEnforceIf(b)  # Thêm ràng buộc x[4] ≠ 2 nếu b = True

# Tạo solver
solver = cp_model.CpSolver()
solver.parameters.search_branching = cp_model.FIXED_SEARCH

# In nghiệm
vars = [x[i] for i in range(5)]
solution_printer = VarArraySolutionPrinter(vars)
solver.SearchForAllSolutions(model, solution_printer)
