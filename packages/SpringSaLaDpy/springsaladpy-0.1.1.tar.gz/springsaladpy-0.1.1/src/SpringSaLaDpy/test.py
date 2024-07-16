import pandas as pd
import csv

path = r'Examples\Nephrin-Nck-NWasp\Final_version_test_SIMULATIONS\Simulation0_SIM_SIMULATIONS\Simulation0_SIM_FOLDER\data\Run0\SiteIDs.csv'

data_dict = {}

with open(path, mode='r') as file:
    csv_reader = csv.reader(file)

    for row in csv_reader:
        key = row[0]
        value = row[1].split()
        value = [value[0], value[4]]
        data_dict[key] = value

print(data_dict['100000000'])