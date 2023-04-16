# implement python code to simulate a logistic map, and create a plot of x versus r.
# only showed one path - asked to plot the entire bifurcation set - failed for unclear reasons


import matplotlib.pyplot as plt

def logistic_map(x, r):
    return r * x * (1 - x)

# Simulation parameters
r_values = [r/100 for r in range(1000, 4001)]  # range of r values
x0 = 0.5  # initial value of x
n = 1000  # number of iterations per r value
transient = 200  # number of transient iterations to discard

# Run simulation for each r value
x_values = []
for r in r_values:
    x = x0
    for i in range(transient + n):
        x = logistic_map(x, r)
        if i >= transient:
            x_values.append((r, x))

# Create plot of bifurcation set
rs = [x[0] for x in x_values]
xs = [x[1] for x in x_values]
plt.plot(rs, xs, 'b.', markersize=0.1)
plt.xlabel('r')
plt.ylabel('x')
plt.title('Bifurcation Diagram of Logistic Map')
plt.show()
