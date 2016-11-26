#current working version


#the below imports different libraries, allowing different functions to happen. 
#Requests is for sending and receving html requests. I use both GET and POST in the below script to pinch the HTML from thepiratebay and to log into pogdesign
#datetime is a library for referencing dates, used for editing the date format on pogdesign into something the code can read and compare to todays date.
#Beautifulsoup is for scraping and parsing the html on the website referenced by the get request.
#os allows you to mess with your os in different ways, basic stuff like getting file names and sizes, in this case i use it to open the torrent link, which auto opens my 
#bit torrent client if its not already open.
#time is a library for referencing time, i use it to pause the script for 7 seconds each loop, to allow the get request to refresh

import requests
import datetime
from bs4 import BeautifulSoup
import os
import time

#this is a custom function which goes and searches pirate bay for the torrent that is referenced (later), parses the html to find the magnet link of the top torrent, and
#uses os.startfile to open it.

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

	
#logs into my pogdesign account using requests to post the login and password.
	
with requests.Session() as c:
    url = "https://www.pogdesign.co.uk/cat/login"
    #enter your username and password as string below.
    uName = ""
    pWord = ""
    c.get(url)
    login_data = dict(username=uName, password=pWord, sub_login="")
    c.post(url, data=login_data, headers={"Referer":"https://www.pogdesign.co.uk/cat/login"})
    page = c.get("https://www.pogdesign.co.uk/cat")
    #takes the html data from the pogdesign page
    soup = BeautifulSoup(page.content)
    
    showList = []
    
    #edits the date for each day shown on the pogdesign calendar into the date formate which the datetime library uses, to see if its before today.
    for j in soup.find_all("div",class_="day"):
        jdate = j.get('id')
        jdate = jdate[2:]
        if len(jdate) == 9:
            jdate = str(0) + jdate
        jDay = int(jdate[0:2])
        jMonth = int(jdate [3:5])
        jYear = int(jdate [6:10])
        jdate = datetime.date(jYear,jMonth,jDay)
        
        if jdate > datetime.date.today():
            break
        
		#theres several different types of episode 'class' as pogdesign defines them, betweeen normal episode, series premire, season premire and season finale.
		#the below 4 loops test each type of episode class to make sure they're all picked up, and add it to a list called ShowList.
		
        for i in j.find_all("div",class_="ep info"):
            fix = i.get_text()
            showList.append(fix)
                
        for v in j.find_all("div",class_="ep info fep"):
            fix = v.get_text()
            showList.append(fix)
                
        for p in j.find_all("div",class_="ep info pep"):
            fix = p.get_text()
            showList.append(fix)
        
        for l in j.find_all("div",class_="ep info lep"):
            fix = l.get_text()
            showList.append(fix)
                
    #theres also a slightly different class if an episode is available today as opposed to any other date, and the below loop adds those shows to a list.            
    for j in soup.find_all("div",class_="today"):
        for i in j.find_all("div",class_="ep"):
            fix = i.get_text()
            showList.append(fix)

			
#edits the format for each show in the list, which includes a load of unnessesary linebreaks between the show names and the episode numbers.
#also adds the %20 in place of the spaces, ready to be added to the piratebay url as seen in the GetTorrent function			
for count, item in enumerate(showList):
    if '\n' in item:
        item = item.strip('\n')
        item = item.strip()
        item = item.replace('\n',' ')
        item = item.replace(' ','%20')

		
#loops through each show in the list, prints the name so i can see whats being downloaded, and runs the gettorrent function on the showname.
#then it waits 7 seconds so it has time to refresh the request each time. no particular reason for the 7 seconds, i figured it would need at least 5 but no more than 10.
for Show in showList:
    print Show
    GetTorrent(Show)
    time.sleep(7)
