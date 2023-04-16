# create python code to simulate a drift diffusion model with collapsing bounds. 
# - please return the entire timeseries of diffusion steps from the function.

import numpy as np
import matplotlib.pyplot as plt

def simulate_ddm_with_collapsing_bounds(drift_rate, boundary_func, noise_std, time_step, max_time):
    decision_time = 0
    evidence = [0]
    time_series = [0]
    
    while decision_time < max_time:
        decision_time += time_step
        noise = np.random.normal(0, noise_std)
        delta_evidence = drift_rate * time_step + noise
        current_evidence = evidence[-1] + delta_evidence
        
        upper_bound = boundary_func(decision_time, 'upper')
        lower_bound = boundary_func(decision_time, 'lower')
        
        if current_evidence >= upper_bound:
            return {'decision': 1, 'evidence': evidence, 'decision_time': decision_time, 'time_series': time_series}
        elif current_evidence <= lower_bound:
            return {'decision': -1, 'evidence': evidence, 'decision_time': decision_time, 'time_series': time_series}
        
        evidence.append(current_evidence)
        time_series.append(decision_time)
    
    return {'decision': 0, 'evidence': evidence, 'decision_time': decision_time, 'time_series': time_series}

def linear_collapsing_bounds(time, bound_type, start, end, max_time):
    if bound_type == 'upper':
        return start + (end - start) * (time / max_time)
    elif bound_type == 'lower':
        return start - (end - start) * (time / max_time)

drift_rate = 0.5
noise_std = 0.1
time_step = 0.01
max_time = 5
upper_bound_start = 2
upper_bound_end = 1

boundary_func = lambda time, bound_type: linear_collapsing_bounds(time, bound_type, upper_bound_start, upper_bound_end, max_time)
simulation_result = simulate_ddm_with_collapsing_bounds(drift_rate, boundary_func, noise_std, time_step, max_time)

plt.plot(simulation_result['time_series'], simulation_result['evidence'])
plt.xlabel('Time')
plt.ylabel('Evidence')
plt.title(f'Drift Diffusion Model with Collapsing Bounds (Decision: {simulation_result["decision"]})')
plt.show()
