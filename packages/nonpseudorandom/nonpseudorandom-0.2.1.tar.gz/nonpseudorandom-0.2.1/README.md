# NonPseudoRandom

[![PyPI version](https://img.shields.io/pypi/v/nonpseudorandom.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/nonpseudorandom/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/nonpseudorandom.svg?logo=python&logoColor=FFE873)](https://pypi.org/project/nonpseudorandom/)
[![PyPI downloads](https://img.shields.io/pypi/dm/nonpseudorandom.svg)](https://pypistats.org/packages/nonpseudorandom)

NonPseudoRandom is a Python package that generates true random numbers using sensor noise from your local system. It serves as a drop-in replacement for Python's native `random` module.

## Supported Sensors

NonPseudoRandom utilizes various types of system sensors to generate randomness. The supported sensor types are as follows:

| Sensor Type        | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| CPU Temperature    | Measures the temperature of the CPU using `psutil`.                   |
| Microphone Noise   | Captures ambient noise from the microphone using `sounddevice`.       |
| Webcam Noise       | Captures visual noise from the webcam using `opencv-python`.          |

## Installation

You can install NonPseudoRandom via pip:

```sh
pip install nonpseudorandom
```

## Usage

NonPseudoRandom can be used as a drop-in replacement for Python's built-in `random` module. Here are some examples:

### Example 1: Generating a Random Float

```python
import nonpseudorandom as random

print(random.random())  # Generate a random float in [0.0, 1.0)
```

### Example 2: Generating a Random Integer

```python
import nonpseudorandom as random

print(random.randint(1, 10))  # Generate a random integer between 1 and 10
```

### Example 3: Choosing a Random Element from a List

```python
import nonpseudorandom as random

print(random.choice(['a', 'b', 'c']))  # Randomly select an element from a list
```

### Example 4: Shuffling a List

```python
import nonpseudorandom as random

my_list = [1, 2, 3, 4, 5]
random.shuffle(my_list)
print(my_list)  # The list will be shuffled
```

### Example 5: Sampling from a Population

```python
import nonpseudorandom as random

population = [1, 2, 3, 4, 5]
sample = random.sample(population, 3)
print(sample)  # Randomly sample 3 unique elements from the population
```

### Example 6: Generating a Random Float in a Range

```python
import nonpseudorandom as random

print(random.uniform(1.0, 10.0))  # Generate a random float between 1.0 and 10.0
```

## License

This project is licensed under the MIT License.
