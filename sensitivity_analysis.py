import pandas as pd
import numpy as np

# Load the Markov model outputs (number of people in each state at each timestep)
ross_data = pd.read_csv("ross_run_results_20250612_201404.csv")
gahv_data = pd.read_csv("gahv_run_results_20250612_200430.csv")

# Load the input data (transition probabilities, costs, and utilities)
transition_df = pd.read_csv('transition_probabilities.csv')
cost_df = pd.read_csv('health_state_costs.csv')
utility_df = pd.read_csv('health_state_utilities.csv')

# Initialize parameters
discount_rate = 0.03  # 3% per year (can be adjusted in sensitivity)
time_horizon = 70  # years

# Discounting function
def discount(value, rate, periods):
    return value / ((1 + rate) ** periods)

# Re-run the Markov model with a new parameter value
def calculate_model(parameter_name, value):
    global ross_data, gahv_data, discount_rate
    
    # Adjust the model based on the parameter change and calculate the new results
    if parameter_name == 'reoperation_cost':
        cost_df['GAHV Cost (€)'] = cost_df['GAHV Cost (€)'].apply(lambda x: x if x != 33000 else value)
        cost_df['Ross Cost (€)'] = cost_df['Ross Cost (€)'].apply(lambda x: x if x != 57670 else value)
    elif parameter_name == 'utility_hpi':
        utility_df['GAHV Utility'] = utility_df['GAHV Utility'].apply(lambda x: x if x != 0.75 else value)
        utility_df['Ross Utility'] = utility_df['Ross Utility'].apply(lambda x: x if x != 0.65 else value)
    elif parameter_name == 'discount_rate':
        discount_rate = value
    
    # Calculate discounted costs and QALYs using the updated values
    total_cost_ross = 0
    total_qalys_ross = 0
    total_cost_gahv = 0
    total_qalys_gahv = 0
    
    for year in range(1, time_horizon + 1):
        # Number of people in each state for Ross and GAHV from the model output
        people_in_states_ross = ross_data.iloc[year - 1, 1:]  # Adjust indexing if necessary
        people_in_states_gahv = gahv_data.iloc[year - 1, 1:]  # Adjust indexing if necessary
        
        # Calculate the total cost for Ross and GAHV for this year
        cost_ross_year = np.sum(people_in_states_ross * cost_df['Ross Cost (€)'].values)
        cost_gahv_year = np.sum(people_in_states_gahv * cost_df['GAHV Cost (€)'].values)
        
        # Calculate the total QALYs for Ross and GAHV for this year
        qalys_ross_year = np.sum(people_in_states_ross * utility_df['Ross Utility'].values)
        qalys_gahv_year = np.sum(people_in_states_gahv * utility_df['GAHV Utility'].values)
        
        # Discount the yearly cost and QALYs
        total_cost_ross += discount(cost_ross_year, discount_rate, year)
        total_qalys_ross += discount(qalys_ross_year, discount_rate, year)
        
        total_cost_gahv += discount(cost_gahv_year, discount_rate, year)
        total_qalys_gahv += discount(qalys_gahv_year, discount_rate, year)

    # Calculate ICER
    icor = (total_cost_gahv - total_cost_ross) / (total_qalys_gahv - total_qalys_ross)

    # Return the new results for comparison
    return total_cost_ross, total_cost_gahv, total_qalys_ross, total_qalys_gahv, icor

# Sensitivity analysis function
def sensitivity_analysis(parameter_name, base_value, variation=0.2):
    low = base_value * (1 - variation)
    high = base_value * (1 + variation)
    
    # Recalculate the model with low and high values for this parameter
    low_result = calculate_model(parameter_name, low)
    high_result = calculate_model(parameter_name, high)
    
    return low_result, high_result

# Sensitivity analysis for Reoperation Cost
reoperation_cost = cost_df['GAHV Cost (€)'].mean()  # Get the average reoperation cost
low_result, high_result = sensitivity_analysis('reoperation_cost', reoperation_cost)

# Sensitivity analysis for Utility Value of HPI (GAHV)
utility_hpi = utility_df['GAHV Utility'].mean()  # Get the average utility for HPI state
low_result_utility, high_result_utility = sensitivity_analysis('utility_hpi', utility_hpi)

# Sensitivity analysis for 3% Discount Rate
low_result_discount, high_result_discount = sensitivity_analysis('discount_rate', discount_rate)

# Results for Reoperation Cost Sensitivity
print("Reoperation Cost Sensitivity Analysis:")
print(f"Low Reoperation Cost Result: {low_result}")
print(f"High Reoperation Cost Result: {high_result}")

# Results for Utility Sensitivity
print("Utility Value Sensitivity Analysis (HPI):")
print(f"Low Utility Value Result: {low_result_utility}")
print(f"High Utility Value Result: {high_result_utility}")

# Results for Discount Rate Sensitivity
print("Discount Rate Sensitivity Analysis:")
print(f"Low Discount Rate Result: {low_result_discount}")
print(f"High Discount Rate Result: {high_result_discount}")
