import requests
import json
import pandas as pd
import time
import os
import datetime
import _pickle
dir_name = os.path.dirname(os.path.realpath(__file__))
#dir_name = ""
pd.set_option('display.max_colwidth', None)
domain = "https://newsblur.com"

siteDict = {5904430:"ABC",4007509:"The Conversation",6282414:"SMH"}

auth = {"username":,"password":}
r = requests.post(domain+"/api/login",data=auth)
authCookie = r.cookies

r = requests.get(domain+"/reader/feeds",cookies=authCookie)
t = json.loads(r.text)
feedIDs = list(t["feeds"].keys())
t["folders"]
folderDict = {}
for d in t["folders"]:
    folderDict.update(d)
folderDict["News"]

r = requests.get(domain+"/reader/starred_story_hashes",cookies=authCookie)
starList = json.loads(r.text)["starred_story_hashes"]
r = requests.post(domain+"/reader/mark_story_hash_as_unread",data={"story_hash":starList},cookies=authCookie)

storyList = []

for j in folderDict["News"]:
    print(siteDict[j])
    cTime = int(time.time())
    page = 1
    while True:
        r = requests.get(domain+"/reader/feed/"+str(j),params={"include_story_content":"false","read_filter":"unread","page":str(page)},cookies=authCookie)
        t = json.loads(r.text)
        if t["stories"]==[]:
            break
        #if page >= 200:
        #    break
        for i in t["stories"]:
            l = [i["story_hash"],siteDict[j],",".join(i["story_tags"]),i["story_date"],i["story_authors"],i["story_title"],0,i["story_permalink"]]
            storyList.append(l)
        print(page)
        page += 1
    #r = requests.post(domain+"/reader/mark_feed_as_read",data={"feed_id":str(j),"cutoff_timestamp":str(cTime),"direction":"older"},cookies=authCookie)

#df=pd.DataFrame(data=storyList)
#df.columns=["Site","Tags","Time","Authors","Title","Verdict","Link"]
#df.to_csv("news.csv",encoding="utf-8-sig")

oldNews = pd.read_csv(dir_name+"\\news.csv",index_col="Hash")

if len(storyList)!=0:
    df=pd.DataFrame(data=storyList)
    df.index = df[0]
    df.drop(0,axis=1,inplace=True)
    df.index.names = ["Hash"]
    df.columns=["Site","Tags","Time","Authors","Title","Verdict","Link"]

    allNews = pd.concat([oldNews,df])
    allNews = allNews[~allNews.index.duplicated(keep='last')]
    
    allNews.loc[starList,"Verdict"]=1
    try:
        allNews.to_csv(dir_name+"\\news.csv",encoding="utf-8-sig")
        with open(dir_name+'\\classifier.pkl', 'rb') as fid:
            c = _pickle.load(fid)
    
        df["TrainTitle"]=[" ".join(a) for a in tuple(zip(df["Site"],df["Tags"],df["Authors"],df["Title"]))]
    
        df["Predicted"]=c.predict(df["TrainTitle"])
        nodf = list(df[df["Predicted"]==0].index)+starList
        r = requests.post(domain+"/reader/mark_story_hashes_as_read",data={"story_hash":nodf},cookies=authCookie)
        r = requests.post(domain+"/reader/mark_story_hash_as_unstarred",data={"story_hash":starList},cookies=authCookie)
    except:
        print("Couldn't write to file.")

