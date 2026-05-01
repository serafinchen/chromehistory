import sqlite3
import shutil
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

def chrome_time_to_datetime(chrome_time):
      return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)


if __name__ == "__main__":
      historyFile = "C:\\Users\\"+os.getenv("USER")+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"

