import unittest
from unittest.mock import patch, MagicMock
from sysbro.postgres_monitor import get_idle_transactions, kill_idle_transactions


class TestPostgresMonitor(unittest.TestCase):

    @patch('sysbro.postgres_monitor.psycopg2.connect')
    def test_get_idle_transactions(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, 'idle', 'SELECT * FROM table;', '00:02:30')]

        conn_info = {'dbname': 'testdb', 'user': 'testuser', 'password': 'testpass', 'host': 'localhost'}
        transactions = get_idle_transactions(conn_info, 150)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][0], 1)

    @patch('sysbro.postgres_monitor.psycopg2.connect')
    def test_kill_idle_transactions(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, 'idle', 'SELECT * FROM table;', '00:02:30')]

        conn_info = {'dbname': 'testdb', 'user': 'testuser', 'password': 'testpass', 'host': 'localhost'}
        kill_idle_transactions(conn_info, 150)
        mock_cursor.execute.assert_called_with("SELECT pg_terminate_backend(1);")
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
