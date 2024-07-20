import time

from src.sumo_experiments import Experiment
from src.sumo_experiments.preset_networks import LilleNetwork
from src.sumo_experiments.traci_util import *

lille = LilleNetwork()
net = lille.NET_FILE
flows = lille.generate_flows(0.1)

exp = Experiment(
    name='test_lille',
    net=net,
    flows=flows
)

t = time.time()

for _ in range(1):
    data = exp.run(simulation_duration=3600*24, gui=True, no_warnings=True, nb_threads=8)

exp.clean_files()

print(time.time() - t)