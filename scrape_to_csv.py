"""
example usages:
    for item in soup.find_all("div", class_="labelrecipe", ):
    for item in soup.find_all("font", attrs={"face": "arial"}):
    webcodevalues = soup.find("span", class_="labelwebcodesvalue")
"""

import bs4 as bs 
import urllib.request 

source = urllib.request.urlopen("https://minecraft.fandom.com/wiki/Block")
soup = bs.BeautifulSoup(source, 'lxml')

blocks = {
    "Blocks": []
}

sections = soup.find_all("div", class_="collapsible-content") 

divcols = sections[0].find_all("div", class_="div-col columns column-width")
divcol = divcols[0]

uls = divcol.find_all("ul")
ul = uls[0]

lis = ul.find_all("li")
for li in lis:
    a = li.find(a)