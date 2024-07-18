import numpy as np
import hashlib
from ._sensors import SensorReader

sensor_reader = SensorReader()

def seed(a=None):
    if a is not None:
        np.random.seed(a)
    else:
        sensor_data = sensor_reader.read_sensors()
        if sensor_data == []:
            raise RuntimeError('sensor data is empty')
        random_seed = hash(sensor_data)
        np.random.seed(random_seed)

def random():
    seed()
    return np.random.random()

def randint(a, b):
    seed()
    return np.random.randint(a, b)

def choice(seq):
    seed()
    return np.random.choice(seq)

def shuffle(seq):
    seed()
    np.random.shuffle(seq)
    return seq

def sample(population, k):
    seed()
    return np.random.choice(population, k, replace=False).tolist()

def uniform(a, b):
    seed()
    return np.random.uniform(a, b)

def hash(obj):
    flattened_items = []
    for item in obj:
        if isinstance(item, np.ndarray):
            flattened_items.extend(item.flatten())
        elif isinstance(item, (int, float)):
            flattened_items.append(item)
        else:
            raise TypeError(f"Unsupported type: {type(item)}")
    
    concatenated_array = np.array(flattened_items)
    array_bytes = concatenated_array.tobytes()
    hash_object = hashlib.sha256(array_bytes)
    hash_digest = hash_object.hexdigest()
    hash_int = int(hash_digest, 16) % (2**32)
    return hash_int