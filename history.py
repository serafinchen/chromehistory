import sqlite3
import shutil
import datetime

def chrome_time_to_datetime(chrome_time):
      return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=chrome_time)


if __name__ == "__main__":
      
      historyFile = "C:\\Users\\seraf\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
      shutil.copy2(historyFile, "history_copy.db")
      c = sqlite3.connect("history_copy.db")
      cursor = c.cursor()

      selectStatement = """
      SELECT visits.visit_time, urls.url, urls.title
      FROM visits
      JOIN urls ON visits.url = urls.id
      ORDER BY visits.visit_time ASC
      LIMIT 50;
      """

      for row in cursor.execute(selectStatement):
            time = chrome_time_to_datetime(row[0])
            print (str(time)+"URL:"+str(row[1])+str(row[2])+"\n")  