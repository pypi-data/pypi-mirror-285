import time
import shutil

from src.sumo_experiments import Experiment
from src.sumo_experiments.preset_networks import BolognaNetwork
from src.sumo_experiments.traci_util import *
from src.sumo_experiments.strategies.bologna import *
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns


INTERVAL_METRICS = 0.2

# Fixed simulation parameter
EXP_DURATION = 3600
TRAINING_DURATION = 3600 * 6
TEMP_RES_FOLDER = 'temp_results'
PLOT_FOLDER = 'plots'
DATA_FILE = 'res_bologna.csv'
METRICS_FILE = 'metrics_bologna.csv'
SQUARE_SIZE = 3
LANE_LENGTH = 200
YELLOW_TIME = 3
MAX_SPEED = 50
BOOLEAN_DETECTOR_LENGTH = 20

# Variable simulation parameter
nb_exps = 29
seeds = [i for i in range(1000)]
loads = [i / 100 for i in range(1, 200)]

# Strategies parameters
strategies = [
    'Fixed',
    'Max_pressure',
    'SOTL',
    'Acolight'
]
max_green_times = [i for i in range(10, 121, 10)]                # From 10 to 120
thresholds_switch = [i for i in range(120, 600, 20)]             # From 120 to 599
thresholds_force = [i for i in range(30, 70, 5)]                 # From 30 to 70

t = time.time()
# Create temp folder
if os.path.exists(TEMP_RES_FOLDER):
    shutil.rmtree(TEMP_RES_FOLDER)
os.makedirs(TEMP_RES_FOLDER)

cpt = 1
for strategy in strategies:
    n = 0
    while n < nb_exps:

            k = np.random.choice([0.01 * i for i in range(200)])

            # Create experiment objects
            bologna = BolognaNetwork()
            bologna.generate_flows(k)

            if strategy == 'Fixed':
                phase_times = {}
                phase_times['210'] = [np.random.choice(max_green_times) for _ in range(3)]
                phase_times['219'] = [np.random.choice(max_green_times) for _ in range(3)]
                phase_times['209'] = [np.random.choice(max_green_times) for _ in range(2)]
                phase_times['220'] = [np.random.choice(max_green_times) for _ in range(2)]
                phase_times['221'] = [np.random.choice(max_green_times) for _ in range(2)]
                phase_times['235'] = [np.random.choice(max_green_times) for _ in range(4)]
                phase_times['273'] = [np.random.choice(max_green_times) for _ in range(3)]
                strat = FixedTimeStrategyBologna(phase_times)
                phase_times_label = ''
                for i in ['209', '210', '219', '220', '221', '235', '273']:
                    phase_times_label += str(phase_times[i]) + '$'
                str_params = f'phase_times={phase_times_label}'
            elif strategy == 'Max_pressure':
                periods = {}
                periods_label = ''
                for i in ['209', '210', '219', '220', '221', '235', '273']:
                    periods[i] = np.random.choice(max_green_times)
                    periods_label += str(periods[i]) + '$'
                strat = MaxPressureStrategyBologna(periods)
                str_params = f'periods={periods_label}'
            elif strategy == 'SOTL':
                t_switch = {}
                t_force = {}
                min_duration = {}
                t_force_label = ''
                t_switch_label = ''
                min_durations_label = ''
                for i in ['209', '210', '219', '220', '221', '235', '273']:
                    t_switch[i] = np.random.choice(thresholds_switch)
                    t_switch_label += str(t_switch[i]) + '$'
                    t_force[i] = np.random.choice(thresholds_force)
                    t_force_label += str(t_force[i]) + '$'
                    min_duration[i] = np.random.choice(max_green_times)
                    min_durations_label += str(min_duration[i]) + '$'
                strat = SotlStrategyBologna(t_switch, t_force, min_duration)
                str_params = f'threshold_switch={t_switch_label}!threshold_force={t_force_label}!min_phase_duration={min_durations_label}'
            elif strategy == 'Acolight':
                max_duration = {}
                min_duration = {}
                max_duration_label = ''
                min_durations_label = ''
                for i in ['209', '210', '219', '220', '221', '235', '273']:
                    max_duration[i] = np.random.choice(max_green_times)
                    max_duration_label += str(max_duration[i]) + '$'
                    min_duration[i] = np.random.choice(range(9, max_duration[i] if max_duration[i] <= 30 else 30))
                    min_durations_label += str(min_duration[i]) + '$'
                strat = AcolightStrategyBologna(min_duration, max_duration)
                str_params = f'min_phases_duration={min_durations_label}!max_phases_duration={max_duration_label}'

            # Traci functions
            tw = TraciWrapper(EXP_DURATION)
            tw.add_stats_function(get_speed_data)
            tw.add_stats_function(get_co2_emissions_data)
            tw.add_behavioural_function(strat.run_all_agents)

            # Run
            exp_name = f'{strategy}-{str(k)}-{str_params}'
            exp = Experiment(
                name=exp_name,
                full_line_command=bologna.FULL_LINE_COMMAND
            )

            try:
                data = exp.run_traci(tw.final_function, gui=False, no_warnings=True, nb_threads=8)
                data.to_csv(f'{TEMP_RES_FOLDER}/{exp_name}.csv')

                print(f"Done experiment {cpt} on {nb_exps * len(strategies)}.")
                cpt += 1
                n += 1
            except:
                pass

            exp.clean_files()

# Get results files names
res_files = os.listdir(TEMP_RES_FOLDER)

results = []

print("\nComputing aggregations of results.")
for filename in res_files:

    data = pd.read_csv(f'{TEMP_RES_FOLDER}/{filename}')
    key = filename.split('.csv')[0]

    method = key.split('-')[0]
    load = float(key.split('-')[1])
    params = key.split('-')[2]

    # Compute mean travel time
    try:
        mean_tt_data = data[['mean_travel_time', 'mean_CO2_per_travel', 'exiting_vehicles']][data['exiting_vehicles'] != 0].to_numpy()
        mean_travel_time = np.average(mean_tt_data[:, 0], weights=mean_tt_data[:, 2])
        # Compute mean co2 emissions per travel
        mean_co2_emissions = np.average(mean_tt_data[:, 1], weights=mean_tt_data[:, 2])

        results.append([method, load, mean_travel_time, mean_co2_emissions, params])
    except ZeroDivisionError:
        pass

columns = ['method', 'load', 'mean_travel_time', 'mean_co2_emissions_travel', 'params']
data_results = pd.DataFrame(results, columns=columns)
data_results.to_csv(DATA_FILE)

if not os.path.exists(PLOT_FOLDER):
    os.makedirs(PLOT_FOLDER)

data = pd.read_csv(DATA_FILE)

# Get potential and intensity
loads = [int(load * 10) for load in loads]
nb_intervals = len(range(min(loads), max(loads), int(INTERVAL_METRICS * 10)))
results = {}
for strategy in strategies:
    results[strategy] = {'potential_travel_time': 0.0,
                         'potential_co2_emissions': 0.0,
                         'intensity_travel_time': 0.0,
                         'intensity_co2_emissions': 0.0}
    current_data = data[data['method'] == strategy]
    for i in range(min(loads), max(loads), int(INTERVAL_METRICS * 10)):
        interval_data = current_data[np.logical_and(current_data['load'] >= i/10, current_data['load'] < i/10 + INTERVAL_METRICS)]
        results[strategy]['potential_travel_time'] += min(interval_data['mean_travel_time']) if len(interval_data['mean_travel_time']) > 0 else 0
        results[strategy]['potential_co2_emissions'] += min(interval_data['mean_co2_emissions_travel']) if len(interval_data['mean_co2_emissions_travel']) > 0 else 0
        results[strategy]['intensity_travel_time'] += np.mean([abs(j - np.mean(interval_data['mean_travel_time'])) for j in interval_data['mean_travel_time']]) if len(interval_data['mean_travel_time']) > 0 else 0
        results[strategy]['intensity_co2_emissions'] += np.mean([abs(j - np.mean(interval_data['mean_co2_emissions_travel'])) for j in interval_data['mean_co2_emissions_travel']]) if len(interval_data['mean_co2_emissions_travel']) > 0 else 0
    results[strategy]['potential_travel_time'] = results[strategy]['potential_travel_time'] / nb_intervals
    results[strategy]['potential_co2_emissions'] = results[strategy]['potential_co2_emissions'] / nb_intervals

final_results = []
for strategy in strategies:
    potential_travel_time = round(results[strategy]['potential_travel_time'], 2)
    potential_emissions = round(results[strategy]['potential_co2_emissions'], 2)
    intensity_travel_time = round(results[strategy]['intensity_travel_time'], 2)
    intensity_emissions = round(results[strategy]['intensity_co2_emissions'], 2)
    final_results.append([strategy, potential_travel_time, potential_emissions, intensity_travel_time, intensity_emissions])
final_results = pd.DataFrame(final_results, columns=['Strategy',
                                                     'Potential travel time',
                                                     'Potential CO2 emissions',
                                                     'Intensity travel time',
                                                     'Intensity CO2 emissions'])
final_results.to_csv(METRICS_FILE, index=False)

data['method'] = data['method'].map(lambda x: x.replace('_', ' '))
data['mean_co2_emissions_travel'] = data['mean_co2_emissions_travel'].map(lambda x: x / 10**6)

matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)
fig, (ax1, ax2) = plt.subplots(1, 2)
markers = ['X', '^', 'D', 'o', 'P']
colors = ['#e41a1c', '#636363', '#4daf4a', '#393b79', '#e6ab02']
sns.scatterplot(ax=ax1, x='load', y='mean_travel_time', data=data, style='method', hue='method', palette=colors, markers=markers, s=84)
sns.scatterplot(ax=ax2, x='load', y='mean_co2_emissions_travel', data=data, style='method', hue='method', palette=colors, markers=markers, s=84)
# g = sns.pairplot(data=data,
#              hue='method',
#              x_vars=['flow'],# 'asymetry', 'complexity'],
#              y_vars=['mean_travel_time', 'mean_speed', 'mean_co2_emissions'])
#
# g.fig.suptitle("3x3 grid", y=1.08)
fig.set_size_inches(45, 15)
ax1.set_xlabel('Load (in coefficient of real traffic)', fontsize=30, labelpad=20)
ax2.set_xlabel('Load (in coefficient of real traffic)', fontsize=30, labelpad=20)
ax1.set_ylabel('Mean travel time (in s)', fontsize=30, labelpad=20)
ax1.set_ylim(0, 2000)
ax2.set_ylabel('CO2 emissions per travel (in Kg)', fontsize=30, labelpad=20)
ax2.set_ylim(0, 4)
ax1.legend(fontsize=24)
ax2.legend(fontsize=24)
plt.savefig(f'{PLOT_FOLDER}/plot_acolight.png')
plt.show()


duration = time.time() - t
hours = int(duration // 3600)
minutes = int((duration % 3600) // 60)
print(f"Durée de l'expérience : {hours} heures et {minutes} minutes.")