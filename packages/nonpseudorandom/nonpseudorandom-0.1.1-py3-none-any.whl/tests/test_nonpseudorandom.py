import unittest
import nonpseudorandom as random

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

if __name__ == '__main__':
    unittest.main()
