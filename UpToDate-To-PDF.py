import time
import base64
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import re

#input login & password
LOGIN_NAME=''
PASSWORD=''


# activate headless mode
op = webdriver.ChromeOptions()
op.add_argument('headless')
browser = webdriver.Chrome(options=op)


# search keywords
searchedKeyword = input('Search UpToDate: ')

linkList = list()     # list to store links that come up when the keyword is searched
x = 1     # value to be used for enumeration of options

#log in to UpToDate account
browser.get('https://www.uptodate.com/login')
browser.find_element(By.ID, 'userName').send_keys(LOGIN_NAME)
browser.find_element(By.ID, 'password').send_keys(PASSWORD, Keys.ENTER)
print(f'\n>>> Logged in as {LOGIN_NAME}.')


# time module is utilized to wait for javaScript pages to fully load.
# selenium's expected_conditions function wouldn't work properly.
time.sleep(3)


# get all anchor tags as list
browser.find_element(By.ID, 'tbSearch').send_keys(searchedKeyword, Keys.ENTER)
time.sleep(3)
soup = bs(browser.page_source, 'lxml')
# search-result-subhit-container class is removed to obviate duplicates
subhitContainer = soup.find_all(class_='search-result-subhit-container')
for i in subhitContainer:
    i.extract()

# regex pattern -> grabs anchor tags that end with 'rank=[int]'
pattern = re.compile('.*rank=[0-9]{1,2}')

# links(href) are extracted off the anchor tags and made into a list
for i in soup.find_all('a'):
    matches = re.finditer(pattern, str(i.get('href')))
    for e in matches:
        linkList.append(e.group(0))


print('\n*** Choose which of the following UpToDate articles you\'d like save as PDF.\n')
# regex pattern -> parses url to make it into a multiple choice dropdown list
finetunePattern = re.compile('^/.+\?')
for i in linkList:
    matchesFineTuned = re.finditer(finetunePattern, i)
#enumerate the options
    for e in matchesFineTuned:
        print('(',x, ') ', e.group(0).replace('/contents/', '').replace('?', '').replace('-', ' '))
        x+=1


# selects an option from the list
key = int(input('\nEnter key: ')) - 1
browser.get(f'https://www.uptodate.com{linkList[key]}')
time.sleep(2)
soup = bs(browser.page_source, 'lxml')
printLink = soup.find_all(id='printTopic')[0].get('href')
browser.get(f'https://www.uptodate.com{printLink}')


#creates the title of the PDF document
finalTitle = re.search(finetunePattern, str(printLink)).group(0).replace('/contents/', '').replace('?', '').replace('-', ' ').replace('/print', '')


time.sleep(1)
print('\n>>> Saving as PDF.')
time.sleep(2)


# PDF is saved in the same directory as the py file. Target location may be modified.
pdf = browser.execute_cdp_cmd("Page.printToPDF", {
    "printBackground": True, "scalingType": 2,
    "scaling": "100"
})
with open(f"{finalTitle}.pdf", "wb") as f:
    f.write(base64.b64decode(pdf['data']))
    f.close()

print('\n>>> Done.')

time.sleep(3)
browser.quit()
