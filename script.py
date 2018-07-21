# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 22:03:20 2018

@author: Turner_prize
"""

import re
import os
from json import dumps
import datetime
import time
from bs4 import BeautifulSoup
import requests
from rarbgapi import RarbgAPI

# Replace hostname, transmission-username and transmission-password

TVDB = "C:\Users\Turner_prize\Desktop\TVDBList2.txt"
MyDir = "D:\Dan\TV"


def AmendList(ShowList):
    f = open(TVDB, 'r')
    ShowDatabase = f.read().splitlines()
    for Show in ShowList:
        if not Show in ShowDatabase:
            ShowDatabase.append(Show)
    with open(TVDB, 'w') as outfile:
        for item in ShowDatabase:
            outfile.write("%s\n" % item)
    return ShowDatabase

def CreateShowList(MyPath):
#checks folder for TV Shows, adds them to list to compare later.
    ShowList= []
    ShowNames = []
    findit = re.compile(r'.S\d{1,2}E\d{1,2}')
    sYear = re.compile(r'\d{4}\s')
    for dirname, dirnames, filenames in os.walk(MyPath,topdown=False):
        for files in filenames:
            foundit = re.search(findit,files.upper())
            if foundit:
                rubbish = foundit.group()
                x = files.upper().find(rubbish) #x is an integer
                MyShow =  files[:x].title() + rubbish
                MyShow = MyShow.replace("."," ")
                foundYear = re.search(sYear,MyShow)
                if foundYear:
                    MyShow = re.sub(r'\d{4}\s',"",MyShow)
                if not files[:x].title() in ShowNames:
                    ShowList.append(MyShow.upper())
    ShowList = sorted(ShowList)
    ShowList = AmendList(ShowList)
    return ShowList


def GetMyDates(x):
    NewDate = datetime.date.today()
    if x > 0:
        dt = datetime.timedelta(days=1)
        NewDate = datetime.date(NewDate.year, NewDate.month, 1) - dt
    if x > 1:
        NewDate = datetime.date(NewDate.year, NewDate.month, 1) - dt
    NewDate = NewDate.strftime("%m-%Y")
    NewDate = NewDate.lstrip('0')
    return NewDate

def GetPogDesignURL():
    for i in range(3):
        MyDate = GetMyDates(i)
        print MyDate
        myURL = "http://www.pogdesign.co.uk/cat/" + MyDate
        MyList = ShowRequest(myURL)
        yield MyList
        
def ShowRequest(website):
    NewShows = []
    RegDate = re.compile(r'\d{1,2}_\d{1,2}_\d{4}')
    with requests.Session() as c:
        url = "https://www.pogdesign.co.uk/cat/login"
        uName = ""
        pWord = ""
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

        for i in GetShowString("ep info",j):
            NewShows.append(i)
        for i in GetShowString("ep info fep",j):
            NewShows.append(i)
        for i in GetShowString("ep info pep",j):
            NewShows.append(i)
        for i in GetShowString("ep info lep",j):
            NewShows.append(i)

    for j in soup.find_all("div",class_="today"):
        for i in GetShowString("ep",j):
            NewShows.append(i)

    NewShows = filter(None, NewShows)
    NewShows = [w.strip('\n') for w in NewShows]
    NewShows = [w.strip() for w in NewShows]
    NewShows = [w.replace('\n'," ") for w in NewShows]
    return NewShows


def GetShowString(iClass,showz):
    for i in showz.find_all("div",class_=iClass):
        fix = i.get_text()
        yield fix

def AddToList(NewShow):
    #this is similar to AmendList, but is specifically for when a torrent file is found.
    f = open(TVDB, 'r')
    ShowDatabase = f.read().splitlines()
    ShowDatabase.append(NewShow.upper())
    with open(TVDB, 'w') as outfile:
        for item in ShowDatabase:
            outfile.write("%s\n" % item)


def GetTorrent(MyShow):
    x = RarbgAPI()
    myresponse = x.search(MyShow,category=41)
    os.startfile(myresponse[0].download)
    AddToList(MyShow)

ShowList = CreateShowList(MyDir)

ShowDatabase = sorted(ShowList)

with open(TVDB, 'w') as outfile:
    for item in ShowDatabase:
        outfile.write("%s\n" % item)

for Shows in GetPogDesignURL():
    for Show in Shows:
       if not Show.upper() in ShowList:
               print Show.upper() 
               GetTorrent(Show)
               time.sleep(5)

