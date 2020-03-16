import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import pandas as pd
import tracking_report.display_report as display_report

class TestDisplayReport(unittest.TestCase):

    def test_read_log(self):
        with self.assertRaises(SystemExit):
            display_report.read_log("teststring.test")

    def test_clean_report(self):
        test_data = {' timestamp ': [' testing ', ' test', ' test Inc '],
                 ' url': [' testing ', ' test', ' test Inc '],
                 'userid ': [' testing ', ' test', ' test Inc ']}

        test_df = pd.DataFrame(test_data)
        test_df = display_report.strip_log(test_df)

        self.assertEqual(test_df.columns[0], 'timestamp')
        self.assertEqual(test_df.columns[1], 'url')
        self.assertEqual(test_df.columns[2], 'userid')

        self.assertEqual(test_df.iloc[0][0], 'testing')
        self.assertEqual(test_df.iloc[1][0], 'test')
        self.assertEqual(test_df.iloc[2][0], 'test Inc')

        with self.assertRaises(SystemExit):
            display_report.strip_log("test")

    def test_set_date_index(self):
        test_data = pd.DataFrame({'timestamp': ['2013-09-01 09:00:00UTC', '2013-09-01 09:00:00UTC', '2013-09-01 09:00:00UTC']})
        log_dataframe = display_report.set_date_index(test_data)
        self.assertTrue(log_dataframe.index.is_all_dates)

        with self.assertRaises(SystemExit):
            test_data = pd.DataFrame({'timestamp': ['2013-09-01 09:00:00UTC', 'test', '2013-09-01 09:00:00UTC ']})
            display_report.set_date_index(test_data)

    def test_aggregate_log(self):
        test_data = pd.DataFrame(
            {'timestamp': ['2013-09-01 09:300:00UTC', '2013-09-01 09:30:00UTC', '2013-09-01 10:00:00UTC'],
                 'url': ['/help.html', '/help.html', '/help.html'],
                 'userid': ['1234', '1234', 'test_user1']})
        test_data.set_index(['timestamp'], inplace = True)

        from_date = "2013-09-01 09:00:00"
        to_date = "2013-09-01 09:59:59"
        log_dataframe = display_report.aggregate_log(test_data, from_date, to_date)

        self.assertEqual(log_dataframe.columns[0], 'url')
        self.assertEqual(log_dataframe.columns[1], 'page views')
        self.assertEqual(log_dataframe.columns[2], 'visitors')

        log_dataframe['page views'][0] == 2
        log_dataframe['visitors'][0] == 1

        with self.assertRaises(SystemExit):
            display_report.aggregate_log(pd.DataFrame(), from_date, to_date)

if __name__ == '__main__':
    unittest.main()