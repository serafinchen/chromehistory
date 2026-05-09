import sqlite3
import shutil
import datetime
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ccl_chromium_reader import ChromiumProfileFolder
import pathlib

load_dotenv()
user=os.getenv("USER")
profile_path = pathlib.Path("C:\\Users\\"+user+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default")

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

def get_links_playwright(page, url):
      try:
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            html = page.content()

            soup = BeautifulSoup(html, "html.parser")

            links = set()
            for a in soup.find_all("a", href=True):
                  href = a["href"]
                  links.add(href)

            return links

      except Exception as e:
            print(f"Error at page {url}: {e}")
            return set()


if __name__ == "__main__":

      with ChromiumProfileFolder(profile_path) as profile:
            history_records=profile.iterate_history_records()
            print(x for x in history_records)

      query = """ 
      SELECT visits.visit_time, urls.url 
      FROM visits, urls 
      WHERE visits.url=urls.id
      ORDER BY visits.visit_time DESC
      LIMIT 50; 
      """ 
      history = sql_query(query)
      
      seen_links = set()

      with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for entry in history:
                  url = entry["url"]
                  print(f"{url}")

                  links = get_links_playwright(page, url)
                  overlap = links.intersection(seen_links)

                  if overlap:
                        print("Link appered before")
                        for l in overlap:
                              print("   -", l)
                  else:
                        print("Link didn't appeared before")

                  seen_links.update(links)

            browser.close()

