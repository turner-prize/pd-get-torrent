#creates showlist with name and s/e number to a list. Use when you need to amend exisiting txt json file.
import os
import re
import json
import requests
import datetime
import time
from bs4 import BeautifulSoup
from collections import Counter

RegDate = re.compile(r'\d{1,2}_\d{1,2}_\d{4}')
showList = []
ShowNames = []
data = {}
    
def CreateShowList(MyPath):
#checks folder for TV Shows, adds them to list to compare later.
    findit = re.compile(r'.S\d{1,2}E\d{1,2}')
    sYear = re.compile(r'\d{4}\s')
    for dirname, dirnames, filenames in os.walk(MyPath,topdown=False):
        for files in filenames:
            foundit = re.search(findit,files.upper())
            if foundit:
                rubbish =  foundit.group()
                x = files.upper().find(rubbish) #x is an integer
                MyShow =  files[:x].title() + rubbish
                MyShow = MyShow.replace("."," ")
                foundYear = re.search(sYear,MyShow)
                if foundYear:
                    MyShow = re.sub(r'\d{4}\s',"",MyShow)
                if not files[:x].title() in ShowNames:
                    ShowNames.append(MyShow.upper())
    AmendList(ShowNames)
    
def AmendList(gotShows):
    with open("C:\Users\Turner_prize\Desktop\TVDB.txt", 'r') as infile:
        global data
        data = json.load(infile)
    countr = len(data)
    for Shows in gotShows:
        if not Shows in data.values():
            countr += 1
            data[countr] = Shows
    with open(r'C:\Users\Turner_prize\Desktop\TVDB.txt', 'w') as outfile:
        json.dump(data, outfile)
    
def GetPogDesignURL():
    d = datetime.date.today()
    m = d.month - 2
    if m < 1:
        m = 12
    for i in range(3):
        if m == 13:
            m = 1
        myURL = "http://www.pogdesign.co.uk/cat/" + str(m) + "-2016"
        ShowRequest(myURL)
        m += 1
        
def GetShowString(iClass,showz):
    for i in showz.find_all("div",class_=iClass):
        fix = i.get_text()
        showList.append(fix)

def ShowRequest(website):
    with requests.Session() as c:
        url = "https://www.pogdesign.co.uk/cat/login"
        uName = "" #insert username
        pWord = "" # insert password
        c.get(url)
        login_data = dict(username=uName, password=pWord, sub_login="")
        c.post(url, data=login_data, headers={"Referer":"https://www.pogdesign.co.uk/cat/login"})
        page = c.get(website)
        soup = BeautifulSoup(page.content, "lxml")
   
    for j in soup.find_all("div",class_="day"):
        jdate = j.get('id')
        foundit = re.search(RegDate,jdate)
        if foundit:
            d = datetime.datetime.strptime(foundit.group(), '%d_%m_%Y').date()
        if d > datetime.date.today():
            break
        
        GetShowString("ep info",j)
        GetShowString("ep info fep",j)
        GetShowString("ep info pep",j)
        GetShowString("ep info lep",j)
                
    for j in soup.find_all("div",class_="today"):
        GetShowString("ep",j)
    
    global showList
    showList = [w.strip('\n') for w in showList]
    showList = [w.strip() for w in showList]
    showList = [w.replace('\n'," ") for w in showList]

def GetTorrent(MyShow):
    r = requests.get("https://thepiratebay.org/search/" + MyShow +"/0/99/208")
    soop = BeautifulSoup(r.content)
    for j in soop.find_all("div",class_="detName"):
        if j:
            break
    for a in soop.find_all('a', href=True, title='Download this torrent using magnet'):
        if a:
            break
    os.startfile(a['href'])

MyDir = (r'C:\Users\Turner_prize\Documents\Vuze Downloads')
CreateShowList(MyDir)
GetPogDesignURL()

for shows in showList:
    if not shows.upper() in data.values():
        GetTorrent(shows)
        print shows
        time.sleep(7)

print "Finished"
        
