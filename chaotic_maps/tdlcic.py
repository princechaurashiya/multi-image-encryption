import numpy as np

def tdlcic_map(x0, y0, a, b, num_iterations):
    x, y = np.zeros(num_iterations), np.zeros(num_iterations)
    x[0], y[0] = x0, y0
    for i in range(1, num_iterations):
        x[i] = np.sin(np.pi * a * (y[i-1]**2)) - (np.sin(np.pi * x[i-1]))**2
        y[i] = np.sin(np.pi * b * (x[i-1]**2)) - (np.sin(np.pi * y[i-1]))**2
    return x, y
