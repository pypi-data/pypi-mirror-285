import numpy as np

def location2vec(location_name):
    match location_name:
        case 'Intracellular':
            return np.array([1, 0, 0])
        case 'Extracellular':
            return np.array([0, 1, 0])
        case 'Membrane':
            return np.array([0, 0, 1])