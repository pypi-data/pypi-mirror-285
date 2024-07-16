import unittest
from unittest.mock import patch, MagicMock
from sysbro.redis_cleaner import clean_idle_redis_keys


class TestRedisCleaner(unittest.TestCase):

    @patch('sysbro.redis_cleaner.redis.StrictRedis')
    def test_clean_idle_redis_keys(self, mock_redis):
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.scan_iter.return_value = ['key1', 'key2']
        mock_redis_instance.object.side_effect = [700000, 500000]  # idletimes

        clean_idle_redis_keys(idletime=604800)
        mock_redis_instance.delete.assert_called_once_with('key1')


if __name__ == '__main__':
    unittest.main()
