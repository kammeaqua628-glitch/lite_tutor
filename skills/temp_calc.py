from sympy import symbols, Eq, solve

x = symbols('x')
equation = Eq(x**2 - 5*x + 6, 0)
solutions = solve(equation, x)

print(f"x^2 - 5x + 6 = 0 solutions: {solutions}")
for i, s in enumerate(solutions, 1):
    print(f"  x{i} = {s}")
