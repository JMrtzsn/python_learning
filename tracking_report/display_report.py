import os
import sys
import argparse
import datetime as dt
import pandas as pd

def setup_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Filepath to log file, only takes tab sep files')
    parser.add_argument('from_date', type=lambda d: dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S'),
                        help='Start date for specified period, format: YYYY-MM-DD HH:MM:SS')
    parser.add_argument('to_date', type=lambda d: dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S'),
                        help='End date for specified period, format: YYYY-MM-DD HH:MM:SS')
    return parser.parse_args()

def read_log(file_path):
    try:
        return pd.read_csv(file_path, sep='|', dtype=str)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(e)

def strip_log(log_dataframe):
    try:
        log_dataframe.rename(columns=lambda x: x.strip(), inplace=True)
        log_dataframe.dropna(how='all', axis='columns', inplace=True)
        for column in log_dataframe.columns:
            log_dataframe[column] = log_dataframe[column].str.strip()
        return log_dataframe
    except (KeyError, AttributeError) as e:
        sys.exit(f"Error cleaning data - Error: {e}")

def set_date_index(log_dataframe):
    try:
        log_dataframe['timestamp'] = pd.to_datetime(log_dataframe['timestamp'])
        log_dataframe.set_index(['timestamp'], inplace = True)
        log_dataframe.sort_index(inplace=True) #in the case of  a whacky logfile

        return log_dataframe if log_dataframe.index.is_all_dates else KeyError
    except (KeyError, ValueError) as e:
        sys.exit(f"Error setting index, required input columns: |timestamp| / all data points need to be dates")

def aggregate_log(log_dataframe, from_date, to_date):
    try:
        grouped = log_dataframe.loc[from_date:to_date].groupby('url')['userid']
        result = grouped.count().reset_index()
        result['visitors'] = grouped.nunique().reset_index()['userid']
        result.rename(columns={'userid':'page views'}, inplace=True)

        return result if not result.empty else sys.exit("No results for that date range")
    except (KeyError, AttributeError) as e:
        sys.exit(f"Error formatting data - Error: {e}")

if __name__ == '__main__':
    #get input vars
    args = setup_argparse()
    log_df = read_log(args.input)

    #format and extract data
    log_df = strip_log(log_df)
    log_df = set_date_index(log_df)
    log_df = aggregate_log(log_df, args.from_date, args.to_date)
    print(log_df)
