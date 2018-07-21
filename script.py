#!/bin/python

import os
import re
import json
import requests
import datetime
import time
from bs4 import BeautifulSoup
#from collections import Counter


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


def GetThisMonth():
    today = datetime.date.today()
    NewDate= today.strftime("%m-%Y")
    NewDate = NewDate.lstrip('0')  
    return NewDate


def GetLastMonth():
    today = datetime.date.today()
    dt = datetime.timedelta(days=1)
    NewDate = datetime.date(today.year, today.month, 1) - dt
    NewDate= NewDate.strftime("%m-%Y")
    NewDate = NewDate.lstrip('0')  
    return NewDate

def Get2Months():

    today = datetime.date.today()
    dt = datetime.timedelta(days=1)
    NewDate = datetime.date(today.year, today.month, 1) - dt
    NewDate = datetime.date(NewDate.year, NewDate.month, 1) - dt
    NewDate= NewDate.strftime("%m-%Y")
    NewDate = NewDate.lstrip('0')  
    return NewDate



def GetPogDesignURL():
        MyDate = GetThisMonth()
        myURL = "http://www.pogdesign.co.uk/cat/" + MyDate
        ShowRequest(myURL)

def ShowRequest(website):
    with requests.Session() as c:
        url = "https://www.pogdesign.co.uk/cat/login"
        uName = "enter username here"
        pWord = "enter password here"
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

    print showList
        
def GetShowString(iClass,showz):
    for i in showz.find_all("div",class_=iClass):
        fix = i.get_text()
        print fix
        showList.append(fix)
        
def AddToList(NewShow):
    #this is similar to AmendList, but is specifically for when a torrent file is found.
    with open("C:\Users\Turner_prize\Desktop\TVDB.txt", 'r') as infile:
        global data
        data = json.load(infile)
    countr = len(data)
    if not NewShow in data.values():
        countr += 1
        NewShow = NewShow.upper()
        data[countr] = NewShow
    with open(r'C:\Users\Turner_prize\Desktop\TVDB.txt', 'w') as outfile:
        json.dump(data, outfile)
    
def GetTorrent(MyShow):
    r = requests.get("https://thepiratebay.org/search/" + MyShow +"/0/99/208")
    soop = BeautifulSoup(r.content, "lxml")
    if "No hits." in soop.text:
        print "No Torrents for " + MyShow + " found."
    else:
        for a in soop.find_all('a', href=True, title='Download this torrent using magnet'):
            if a:
                print a['href']
                os.startfile(a['href'])
                AddToList(MyShow)
                break

def GetTorrentCount():
    r = requests.get("http://localhost:6886/index.tmpl")
    soup = BeautifulSoup(r.text,"lxml")
    Torrents = soup.find(id="tab_selected")
    Torrents = Torrents.text
    Torrents = Torrents.replace("Downloads (","") 
    Torrents = Torrents.replace(")","") 
    return int(Torrents)

MyDir = (r'vuze download path here')
CreateShowList(MyDir)
GetPogDesignURL()

print showList

for shows in showList:
    if not shows.upper() in data.values():
        print shows
        GetTorrent(shows)
        time.sleep(7)
