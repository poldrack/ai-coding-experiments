# Generate python code to simulate a drift diffusion model of response times. Simulate 1000 trials from this model, and estimate the drift rate, boundary separation, and starting point parameters using the EZ-diffusion model.
#
# - on first try it used the hddm package, which failed to pip install on my system.
# - on second try it used the fast-dm package.  it failed because the model() object created in the estimate_parameters_ez_diffusion function does not have a fit() method. 
# - on third try it failed again because it tried to use the nonexisting ddm.fit module. I asked it to create a function to fit the EZ-diffusion model from scratch
# - on fourth try it attempted to create a function to compute the EZ-diffusion model estimates from scratch. however, its math appeared to be incorrect and it gave nonsensican estimates.


import numpy as np
import pandas as pd

def simulate_ddm(num_trials, drift_rate, boundary_separation, starting_point, noise_std_dev=1):
    response_times = []
    choices = []

    for _ in range(num_trials):
        x = starting_point * boundary_separation
        t = 0
        while np.abs(x) < boundary_separation:
            x += drift_rate + np.random.normal(0, noise_std_dev)
            t += 1
        response_times.append(t)
        choices.append(1 if x > 0 else 0)

    data = pd.DataFrame({"rt": response_times, "response": choices})
    return data

def ez_diffusion(rt, correct, s=1):
    rt = np.asarray(rt)
    correct = np.asarray(correct)

    # Calculate mean and variance of correct and error response times
    rt_correct = rt[correct == 1]
    rt_error = rt[correct == 0]
    
    if len(rt_correct) < 2 or len(rt_error) < 2:
        raise ValueError("Not enough correct or error trials to compute EZ-Diffusion parameters")

    mean_rt_correct = np.mean(rt_correct)
    var_rt_correct = np.var(rt_correct)

    mean_rt_error = np.mean(rt_error)
    var_rt_error = np.var(rt_error)

    # Calculate drift rate
    drift_rate = (mean_rt_error - mean_rt_correct) / (s ** 2)

    # Calculate boundary separation
    x = ((mean_rt_correct * mean_rt_error) * (mean_rt_correct - mean_rt_error)) / (s ** 2)
    boundary_separation = (x + np.sqrt(x ** 2 + 4 * (s ** 2) * mean_rt_correct * mean_rt_error)) / (2 * (s ** 2))

    # Calculate starting point
    starting_point = (boundary_separation * (mean_rt_correct - mean_rt_error)) / (2 * s ** 2)

    return drift_rate, boundary_separation, starting_point

if __name__ == "__main__":
    np.random.seed(42)

    num_trials = 1000
    true_drift_rate = 0.5
    true_boundary_separation = 1.5
    true_starting_point = 0.5

    simulated_data = simulate_ddm(
        num_trials,
        true_drift_rate,
        true_boundary_separation,
        true_starting_point,
    )

    rt = simulated_data['rt']
    correct = simulated_data['response']
    estimated_drift_rate, estimated_boundary_separation, estimated_starting_point = ez_diffusion(rt, correct)

    print("Estimated drift rate:", estimated_drift_rate)
    print("Estimated boundary separation:", estimated_boundary_separation)
    print("Estimated starting point:", estimated_starting_point)
