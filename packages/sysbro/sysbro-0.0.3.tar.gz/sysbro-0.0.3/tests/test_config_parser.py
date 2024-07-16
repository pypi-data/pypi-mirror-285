import unittest
import tempfile
from sysbro.config_parser import parse_config


class TestConfigParser(unittest.TestCase):

    def test_parse_config(self):
        config_content = """
        [database]
        db_name = testdb
        db_user = testuser
        db_password = testpass
        db_host = localhost

        [redis]
        redis_url = redis://localhost:6379/0
        """
        with tempfile.NamedTemporaryFile('w+', delete=False) as temp_config:
            temp_config.write(config_content)
            temp_config.flush()
            config = parse_config(temp_config.name)

        self.assertIn('database', config)
        self.assertEqual(config['database']['db_name'], 'testdb')
        self.assertEqual(config['database']['db_user'], 'testuser')
        self.assertEqual(config['database']['db_password'], 'testpass')
        self.assertEqual(config['database']['db_host'], 'localhost')


if __name__ == '__main__':
    unittest.main()
