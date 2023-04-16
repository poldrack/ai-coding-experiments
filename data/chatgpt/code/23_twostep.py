# create python code to analyze human performance on the Daw two-step reinforcement learning task.  the code should take in a data frame with human responses on each trial for each of the two steps along with the outcomes from each step.  it should return the indices of model-based and model-free behavior.
# please create code to generate a synthetic dataset and test it using this function
# this produces a warning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.  please rewrite the code to eliminate this warning
# this results in an error on the line with the pd.concat command

import pandas as pd
import numpy as np
from scipy.optimize import minimize


def daw_two_step_analysis(data):
    """
    Analyzes human performance on the Daw two-step reinforcement learning task.
    
    Args:
        data (pandas.DataFrame): A data frame with human responses on each trial for each of the two steps 
                                 along with the outcomes from each step. The data frame should have the 
                                 following columns:
                                 - subject (int): Subject ID
                                 - trial (int): Trial number
                                 - step (int): Step number (1 or 2)
                                 - outcome (int): Outcome (0 or 1)
                                 - choice (int): Choice (0 or 1)
    
    Returns:
        tuple: A tuple containing the indices of model-based and model-free behavior.
    """
    
    # Group the data by subject and step
    grouped = data.groupby(['subject', 'step'])
    
    # Initialize variables
    n_subjects = len(grouped)
    n_trials = len(data)
    q_model_based = np.zeros((n_subjects, 2))   # Q-values for model-based learning
    q_model_free = np.zeros((n_subjects, 2))    # Q-values for model-free learning
    
    # Define the log-likelihood function for the model-based RL model
    def log_likelihood_model_based(params, data):
        alpha, beta = params
        q_values = np.zeros(2)
        ll = 0
        for i, row in data.iterrows():
            if row['step'] == 1:
                q_values = np.zeros(2)
            q_values[row['choice']] += alpha * (row['outcome'] - q_values[row['choice']])
            if row['step'] == 2:
                prob = np.exp(beta * q_values) / np.sum(np.exp(beta * q_values))
                ll += np.log(prob[row['choice']])
        return -ll
    
    # Define the log-likelihood function for the model-free RL model
    def log_likelihood_model_free(params, data):
        alpha, beta = params
        q_values = np.zeros(2)
        ll = 0
        for i, row in data.iterrows():
            q_values[row['choice']] += alpha * (row['outcome'] - q_values[row['choice']])
            prob = np.exp(beta * q_values) / np.sum(np.exp(beta * q_values))
            ll += np.log(prob[row['choice']])
        return -ll
    
    # Iterate over subjects and steps
    for i, ((subject, step), group) in enumerate(grouped):
        
        # Fit the model-based RL model
        res_mb = minimize(log_likelihood_model_based, [0.5, 1], args=(group,))
        q_model_based[i, :] = res_mb.x
        
        # Fit the model-free RL model
        res_mf = minimize(log_likelihood_model_free, [0.5, 1], args=(group,))
        q_model_free[i, :] = res_mf.x
    
    # Calculate the indices of model-based and model-free behavior
    mb_index = np.mean(q_model_based[:, 0] > q_model_free[:, 0])
    mf_index = np.mean(q_model_free[:, 1] > q_model_based[:, 1])
    
    return (mb_index, mf_index)


def generate_synthetic_data(n_subjects, n_trials):
    """
    Generates a synthetic dataset for the Daw two-step reinforcement learning task.
    
    Args:
        n_subjects (int): Number of subjects
        n_trials (int): Number of trials per subject
    
    Returns:
        pandas.DataFrame: A data frame with synthetic human responses on the Daw two-step reinforcement 
                           learning task. The data frame has the following columns:
                           - subject (int): Subject ID
                           - trial (int): Trial number
                           - step (int): Step number (1 or 2)
                           - outcome (int): Outcome (0 or 1)
                           - choice (int): Choice (0 or 1)
    """
    
    # Define the transition matrix for the two-step task
    transition_matrix = np.array([[0.7, 0.3], [0.3, 0.7]])
    
    # Initialize the data frame
    data = pd.DataFrame(columns=['subject', 'trial', 'step', 'outcome', 'choice'])
    
    # Iterate over subjects
    for subject in range(n_subjects):
        
        # Initialize the Q-values for each step
        q_values = [np.zeros(2), np.zeros(2)]
        
        # Initialize the data frame for the current subject
        subject_data = pd.DataFrame(columns=['subject', 'trial', 'step', 'outcome', 'choice'])
        
        # Iterate over trials
        for trial in range(n_trials):
            
            # Choose the starting step randomly
            if np.random.rand() < 0.5:
                step = 1
            else:
                step = 2
            
            # Choose the outcome of the first choice
            outcome1 = np.random.binomial(1, transition_matrix[step-1, 0])
            
            # Choose the second step based on the outcome of the first choice
            if outcome1 == 0:
                step2 = 1
            else:
                step2 = 2
            
            # Choose the outcome of the second choice
            outcome2 = np.random.binomial(1, transition_matrix[step2-1, 0])
            
            # Choose the second choice based on the Q-values and the temperature parameter
            prob = np.exp(q_values[step2-1]) / np.sum(np.exp(q_values[step2-1]))
            choice2 = np.random.choice(2, p=prob)
            
            # Update the Q-values
            alpha = 0.1
            beta = 2
            q_values[step-1][choice2] += alpha * (outcome2 - q_values[step-1][choice2])
            
            # Add the data to the subject data frame
            subject_data = pd.concat([subject_data, pd.DataFrame({'subject': subject, 'trial': trial+1, 'step': step, 'outcome': outcome1, 'choice': choice2}, columns=['subject', 'trial', 'step', 'outcome', 'choice'], index=[len(subject_data)] * 1)])
        
        # Add the subject data to the data frame
        data = pd.concat([data, subject_data], axis=0)
    
    return data


# Generate a synthetic dataset with 100 subjects and 200 trials per subject
data = generate_synthetic_data(10, 200)

# Analyze the data using the daw_two_step_analysis function
mb_index, mf_index = daw_two_step_analysis(data)

# Print the results
print('Model-based index:', mb_index)
print('Model-free index:', mf_index)
