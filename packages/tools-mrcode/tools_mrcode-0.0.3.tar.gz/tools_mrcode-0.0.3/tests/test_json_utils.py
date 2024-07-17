import src.tools_mrcode.json_util as json_util

import unittest

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_json_path_extr(self):
        age = json_util.json_path_extr("$.user.age", {
            'user': {
                'name': 'mrcode',
                'age': 19
            }
        })

        self.assertEqual(age, 18)

if __name__ == '__main__':
    unittest.main()

