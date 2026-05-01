import sqlite3
import shutil
import datetime

def chrome_time_to_datetime(chrome_time):
      return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)


if __name__ == "__main__":
      pass

