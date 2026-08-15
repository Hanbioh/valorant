from bs4 import BeautifulSoup
import requests
import json

r = requests.get('https://valorant.op.gg/profile/FAKER-KR1', headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
soup = BeautifulSoup(r.text, 'html.parser')

with open("opgg_out.txt", "w", encoding="utf-8") as f:
    f.write(soup.prettify())
