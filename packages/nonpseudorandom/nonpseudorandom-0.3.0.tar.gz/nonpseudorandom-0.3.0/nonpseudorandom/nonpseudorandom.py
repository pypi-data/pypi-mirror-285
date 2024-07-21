import numpy as np
import hashlib
from ._sensors import SensorReader
import random as pseudorandom

class NonPseudoRandom(pseudorandom.Random):

    def __init__(self):
        self.sensor_reader = SensorReader()
        pass

    def seed(self,a=None):
        if a is not None:
            np.random.seed(a)
        else:
            sensor_data = self.sensor_reader.read_sensors()
            if sensor_data == []:
                raise RuntimeError('sensor data is empty')
            random_seed = self.hash(sensor_data)
            np.random.seed(random_seed)

    def hash(self,obj):
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

    def random(self):
        self.seed()
        return np.random.random()



_inst = NonPseudoRandom()

for method_name in dir(_inst):
    if callable(getattr(_inst, method_name)) and not method_name.startswith('__'):
        globals()[method_name] = getattr(_inst, method_name)
