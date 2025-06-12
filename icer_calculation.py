import pandas as pd
import numpy as np

# Load the Markov model outputs (e.g., number of people in each state at each timestep)
ross_data = pd.read_csv("ross_run_results_20250612_201404.csv")
gahv_data = pd.read_csv("gahv_run_results_20250612_200430.csv")

# Load the input data (transition probabilities, costs, and utilities)
transition_df = pd.read_csv('transition_probabilities.csv')
cost_df = pd.read_csv('health_state_costs.csv')
utility_df = pd.read_csv('health_state_utilities.csv')

# Initialize parameters
discount_rate = 0.03  # 3% per year
time_horizon = 70  # years

# Discounting function
def discount(value, rate, periods):
    return value / ((1 + rate) ** periods)

# Initialize variables for total cost and total QALYs calculation
total_cost_ross = 0
total_qalys_ross = 0
total_cost_gahv = 0
total_qalys_gahv = 0

# Iterate through each year/timestep
for year in range(1, time_horizon + 1):
    # Number of people in each state for Ross and GAHV from the model output
    people_in_states_ross = ross_data.iloc[year - 1, 1:]  # Adjust indexing as necessary
    people_in_states_gahv = gahv_data.iloc[year - 1, 1:]  # Adjust indexing as necessary
    
    # Calculate the total cost for Ross and GAHV
    cost_ross_year = np.sum(people_in_states_ross * cost_df['Ross Cost (€)'].values)
    cost_gahv_year = np.sum(people_in_states_gahv * cost_df['GAHV Cost (€)'].values)
    
    # Calculate the total QALYs for Ross and GAHV
    qalys_ross_year = np.sum(people_in_states_ross * utility_df['Ross Utility'].values)
    qalys_gahv_year = np.sum(people_in_states_gahv * utility_df['GAHV Utility'].values)
    
    # Discount the yearly cost and QALYs
    total_cost_ross += discount(cost_ross_year, discount_rate, year)
    total_qalys_ross += discount(qalys_ross_year, discount_rate, year)
    
    total_cost_gahv += discount(cost_gahv_year, discount_rate, year)
    total_qalys_gahv += discount(qalys_gahv_year, discount_rate, year)

# Calculate ICER
icer = (total_cost_gahv - total_cost_ross) / (total_qalys_gahv - total_qalys_ross)

# Output the results
print(f"Total Discounted Cost for Ross Procedure: €{total_cost_ross:,.2f}")
print(f"Total Discounted Cost for GAHV Procedure: €{total_cost_gahv:,.2f}")
print(f"Total Discounted QALYs for Ross Procedure: {total_qalys_ross:,.2f}")
print(f"Total Discounted QALYs for GAHV Procedure: {total_qalys_gahv:,.2f}")
print(f"ICER: €{icer:,.2f} per QALY")
