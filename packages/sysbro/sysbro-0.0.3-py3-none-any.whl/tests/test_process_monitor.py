import unittest
from sysbro.process_monitor import get_process_info, kill_process, suggest_kill_process
import psutil


class TestProcessMonitor(unittest.TestCase):

    def test_get_process_info(self):
        processes = list(get_process_info())
        self.assertIsInstance(processes, list)
        if processes:
            self.assertIn('pid', processes[0])
            self.assertIn('name', processes[0])
            self.assertIn('cpu_percent', processes[0])
            self.assertIn('memory_percent', processes[0])

    def test_kill_process(self):
        proc = psutil.Popen(["sleep", "60"])
        self.assertTrue(proc.is_running())
        kill_process(proc.pid)
        proc.wait(timeout=3)
        self.assertFalse(proc.is_running())

    def test_suggest_kill_process(self):
        # This is more of an integration test and should be tested manually
        suggest_kill_process(0)  # This should print suggestions for all running processes using memory


if __name__ == '__main__':
    unittest.main()
