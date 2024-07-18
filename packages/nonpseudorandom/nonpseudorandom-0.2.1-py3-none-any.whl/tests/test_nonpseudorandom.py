import unittest
import nonpseudorandom as random
import numpy as np

class TestNonPseudoRandom(unittest.TestCase):

    def test_random(self):
        rand_value = random.random()
        self.assertGreaterEqual(rand_value, 0.0)
        self.assertLess(rand_value, 1.0)

    def test_randint(self):
        value = random.randint(1, 10)
        self.assertGreaterEqual(value, 1)
        self.assertLessEqual(value, 10)

    def test_choice(self):
        seq = ['a', 'b', 'c']
        choice = random.choice(seq)
        self.assertIn(choice, seq)

    def test_shuffle(self):
        seq = [1, 2, 3, 4, 5]
        shuffled_seq = random.shuffle(seq)
        self.assertEqual(set(seq), set(shuffled_seq))

    def test_sample(self):
        population = [1, 2, 3, 4, 5]
        sample = random.sample(population, 3)
        self.assertEqual(len(sample), 3)
        for element in sample:
            self.assertIn(element, population)

    def test_uniform(self):
        value = random.uniform(1.0, 10.0)
        self.assertGreaterEqual(value, 1.0)
        self.assertLess(value, 10.0)

    def test_distribution(self):
        samples = [random.random() for _ in range(100)]
        
        mean = np.mean(samples)
        variance = np.var(samples)

        observed, _ = np.histogram(samples, bins=10, range=(0, 1))

        print("Histogram:")
        for i, count in enumerate(observed):
            bin_range = f"{_[i]:.2f} - {_[i+1]:.2f}"
            bar = '#' * int(count)
            print(f"{bin_range.ljust(8)} | {bar}")
        
        self.assertAlmostEqual(mean, 0.5, delta=0.1)
        self.assertAlmostEqual(variance, 1/12, delta=0.1)

        total_samples = len(samples)
        expected = [total_samples / 10] * 10

        # Perform Chi-Square test
        chi_square_statistic = ((observed - expected) ** 2 / expected).sum()
        chi_square_critical = 16.92 # 95% confidence level (9doF)
        self.assertLess(chi_square_statistic, chi_square_critical)


if __name__ == '__main__':
    unittest.main()
