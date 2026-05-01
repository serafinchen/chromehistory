import sqlite3
import shutil
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

def chrome_time_to_datetime(chrome_time):
      return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)

def sql_query(query):
      user = os.getenv("USER")
      historyFile = "C:\\Users\\"+user+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"

      shutil.copy2(historyFile, "history_copy.db") 
      c = sqlite3.connect("history_copy.db") 
      cursor = c.cursor()
      cursor.execute(query)

      rows = cursor.fetchall()
      columns = [col[0] for col in cursor.description]
      result = []
      for row in rows:
            
            row_dict = dict(zip(columns, row))

            if "visit_time" in row_dict:
                  row_dict["visit_time"] = str(
                        chrome_time_to_datetime(row_dict["visit_time"])
                  )

            result.append(row_dict)      

      return result


if __name__ == "__main__":

      selectStatement = """ 
      SELECT visits.visit_time, urls.url, urls.title 
      FROM visits, urls 
      WHERE visits.url=urls.id
      ORDER BY visits.visit_time ASC 
      LIMIT 50; 
      """ 
      print(sql_query(selectStatement))

