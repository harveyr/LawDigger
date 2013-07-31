import urllib2
import re
from bs4 import BeautifulSoup

url = 'http://www.leg.state.or.us/ors/010.html'
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html)

heading_re = re.compile('(\d+\.\d+)\s[\w|\[]')

count = 0
for elem in soup.find_all('p'):
    text = elem.text
    matches = heading_re.match(text.strip())
    if matches:
        section = matches.group(1)
        print('section: {v}'.format(v=section))

    # for b in p.find_all('b'):

        # for s in b.find_all('span'):
        #     for sub_s in s.find_all('span'):
        #         print(sub_s)
