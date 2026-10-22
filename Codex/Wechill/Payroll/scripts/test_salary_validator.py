import importlib.util
import unittest
from datetime import datetime
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("salary_validator.py")
SPEC = importlib.util.spec_from_file_location("salary_validator", MODULE_PATH)
salary_validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(salary_validator)


class PeriodGainCoinTest(unittest.TestCase):
    def test_excludes_only_cycle_start_host_salary_cleanup(self):
        start = datetime(2026, 8, 1, 0, 0, 0)
        rows = [
            {
                "coin": -7000000,
                "source_type": 18,
                "option_type": 203,
                "remark": "host salary",
                "create_time": datetime(2026, 8, 1, 0, 0, 1),
            },
            {
                "coin": 2700000,
                "source_type": 7,
                "option_type": 6,
                "remark": "platform reward",
                "create_time": datetime(2026, 8, 4, 9, 18, 32),
            },
            {
                "coin": -100,
                "source_type": 7,
                "option_type": 6,
                "remark": "business reversal",
                "create_time": datetime(2026, 8, 4, 9, 20, 0),
            },
        ]

        result = salary_validator.summarize_period_gain_coin(rows, start)

        self.assertEqual(result["raw_period_gain_coin"], -4300100)
        self.assertEqual(result["excluded_cycle_start_settlement_debit"], -7000000)
        self.assertEqual(result["period_gain_coin"], 2699900)
        self.assertEqual(result["excluded_record_count"], 1)
        self.assertEqual(result["included_record_count"], 2)

    def test_retains_host_salary_debit_outside_cycle_start_window(self):
        start = datetime(2026, 8, 1, 0, 0, 0)
        row = {
            "coin": -7000000,
            "source_type": 18,
            "option_type": 203,
            "remark": "host salary",
            "create_time": datetime(2026, 8, 1, 0, 10, 0),
        }

        result = salary_validator.summarize_period_gain_coin([row], start)

        self.assertEqual(result["period_gain_coin"], -7000000)
        self.assertEqual(result["excluded_record_count"], 0)


if __name__ == "__main__":
    unittest.main()
