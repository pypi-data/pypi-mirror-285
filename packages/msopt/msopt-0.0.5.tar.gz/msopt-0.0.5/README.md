# Using gurobi syntax for MIP modeling

The syntax of gurobi is very traversal for mip modeling, but the syntax of some open-source solvers and their corresponding API interfaces often uses the conventional naming convention of Python, which is inconvenient for programming with complex constraints.

Therefore, I developed a Python library called gurobi2, which encapsulates commonly used objects such as variable sets, create constraints, constraint sets, and large M methods, and provides a programming experience consistent with gurobipy. I hope to improve the efficiency and experience of programming through this.

For specific API usage, please refer to the official documentation of Gurobi: https://www.gurobi.com/documentation/current/refman/index.html

Here is an example:

```python

from msopt.api import Model, Param, INF, quicksum


m = Model("example", "CBC")

x = m.addVars([1,2,3], vtype="C", name="x")
y = m.addVars([1,2,3], vtype="B", name="y")
z = m.addVars([1,2,3], vtype="I", name="z")

m.addConstr(x.sum() == 1, name="c1")
m.addConstr(y.sum() >= 1, name="c2")
m.addConstr(z[1] == 1, name="c3")

objective = quicksum(x[i] for i in [1,2,3])
m.setObjective(objective, "maximize")

m.setParam(Param.TimeLimit, 10)
m.setParam(Param.MIPGap, 0.01)
m.optimize()

print("status: ", m.status)
print("Objective value: ", m.objVal)
print("x: ", x[1].x, x[2].x, x[3].x)
print("y: ", y[1].x, y[2].x, y[3].x)
print("z: ", z[1].x, z[2].x, z[3].x)

```