# -*- coding: utf-8 -*-
"""
Created on Sat Jun 09 17:13:35 2018

@author: Turner_prize
"""

import datetime
import os
import re
from bs4 import BeautifulSoup
import requests
from rarbgapi import RarbgAPI

def GetTorrent(MyShow):
    x = RarbgAPI()
    myresponse = x.search(MyShow,category=41)
    if not myresponse:
        return False
    else:
        os.startfile(myresponse[0].download)
        return True
    
def CreateSession():
    with requests.Session() as c:
        url = "https://www.pogdesign.co.uk/cat/login"
        uName = "username"
        pWord = "password"
        login_data = dict(username=uName, password=pWord, sub_login="")
        c.post(url, data=login_data, headers={"Referer":"https://www.pogdesign.co.uk/cat/login"})
    return c

def MarkWatched(ShowID):
    c = CreateSession()
    payload = {'watched': "adding", 'shid': ShowID}
    c.post("https://www.pogdesign.co.uk/cat/watchhandle",data=payload)
        
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

def ShowRequest(website,iClass):
	RegDate = re.compile(r'\d{1,2}_\d{1,2}_\d{4}')
	c = CreateSession()
	page = c.get(website)
	soup = BeautifulSoup(page.content, "lxml")
	MyList = []
	for j in soup.find_all("div",class_=iClass):
		jdate = j.get('id')
		foundit = re.search(RegDate,jdate)
		if foundit:
			d = datetime.datetime.strptime(foundit.group(), '%d_%m_%Y').date()
		if d > datetime.date.today():
			break
		for i in j.find_all("div"):
			if not 'checked' in str(i):
				try:
					MyShow = ""
					for x in i.find_all('a'):
						if not MyShow:
							MyShow = x.text
						else:
							MyShow = MyShow + ' ' + x.text
					MyList.append((MyShow,i.input['value']))
				except AttributeError: 
					pass
	return MyList
                
for i in range(1):
	MyDate = GetMyDates(i)
	myURL = "http://www.pogdesign.co.uk/cat/" + MyDate
	x = ShowRequest(myURL,"day")
	for y in x:
		print y[0]
		if GetTorrent(y[0]):
			MarkWatched(y[1])
	w = ShowRequest(myURL,"today")
	for z in w:
		print z[0]
		if GetTorrent(z[0]):
			MarkWatched(z[1])
