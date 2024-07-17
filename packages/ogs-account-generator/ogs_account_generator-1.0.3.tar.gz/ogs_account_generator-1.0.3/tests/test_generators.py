# tests/test_generator.py

import unittest
from ogs_account_generator.generator import generate_random_username

class TestUsernameGeneration(unittest.TestCase):

    def test_generate_random_username(self):
        username = generate_random_username()
        self.assertTrue(username.startswith("Auto_"))

if __name__ == "__main__":
    unittest.main()
