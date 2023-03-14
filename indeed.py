from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

browser = webdriver.Chrome(options=options)


def from_5page_count(keyword):
  base_url = "https://kr.indeed.com/jobs?q="
  count_list = []
  for start in range(50, 91, 10):
    browser.get(f"{base_url}{keyword}&start={start}")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    pagination = soup.find("nav", class_="css-jbuxu0 ecydgvn0")
    pages = pagination.find_all("div", recursive=False)
    count = len(pages)
    if count >= 6 and count <= 7:
      count_list.append(count)
  if len(count_list) == 5:
    return 10
  else:
    return len(count_list)


def get_page_count(keyword):
  base_url = "https://kr.indeed.com/jobs?q="
  browser.get(f"{base_url}{keyword}")
  soup = BeautifulSoup(browser.page_source, "html.parser")
  pagination = soup.find("nav", class_="css-jbuxu0 ecydgvn0")
  if len(pagination) == 0:
    return 1
  pages = pagination.find_all("div", recursive=False)
  count = len(pages)
  if count == 5:
    return 5
  elif count > 5:
    plus_count = from_5page_count(keyword)
    if plus_count == 10:
      return 10
    else:
      return plus_count + 5
  else:
    return count


def extract_indeed_jobs(keyword):
  pages = get_page_count(keyword)
  print("Found", pages, "pages")
  results = []
  for page in range(pages):
    base_url = "https://kr.indeed.com/jobs"
    final_url = f"{base_url}?q={keyword}&start={page*10}"
    print("Requesting", final_url)
    browser.get(final_url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    job_lists = soup.find("ul", class_="jobsearch-ResultsList")
    jobs = job_lists.find_all("li", recursive=False)
    for job in jobs:
      zone = job.find("div", class_="mosaic-zone")
      if zone == None:
        anchor = job.select_one("h2 a")
        title = anchor["aria-label"]
        link = anchor["href"]
        company = job.find("span", class_="companyName")
        location = job.find("div", class_="companyLocation")
        job_data = {
          "link": f"https://kr.indeed.com{link}",
          "company": company.string.replace(",", " "),
          "location": location.string.replace(",", " "),
          "position": title.replace(",", " ")
        }
        results.append(job_data)

  return results
