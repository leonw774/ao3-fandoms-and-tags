import numpy as np
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from collections import Counter 

HIT_THRESOLD = 100
WORKS_NUM = 15

fandoms_urls = [
"Marvel",
"Supernatural",
"Harry%20Potter%20-%20J*d*%20K*d*%20Rowling",
"DCU",
"Sherlock Holmes & Related Fandoms",
"방탄소년단%20%7C%20Bangtan%20Boys%20%7C%20BTS",
"Star Wars",
"Doctor Who & Related Fandoms",
"Voltron: Legendary Defender",
"TOLKIEN%20J*d*%20R*d*%20R*d*%20-%20Works%20*a*%20Related%20Fandoms",
"Dragon Age - All Media Types",
"Star Trek",
"One Direction (Band)",
"僕のヒーローアカデミア%20%7C%20Boku%20no%20Hero%20Academia%20%7C%20My%20Hero%20Academia",
"Haikyuu!!",
"MS Paint Adventures",
"Once Upon a Time (TV)",
"Stargate - All Media Types",
"Naruto",
"Shingeki no Kyojin | Attack on Titan"]

fandoms_names = [
"Marvel",
"Supernatural",
"Harry Potter",
"DCU",
"Sherlock Holmes",
"Bangtan Boys",
"Star Wars",
"Doctor Who",
"Voltron",
"JRR-TOLKIEN",
"Dragon Age",
"Star Trek",
"One Direction",
"My Hero Academia",
"Haikyuu",
"MS Paint Adventures",
"Once Upon a Time",
"Stargate",
"Naruto",
"Attack on Titan"]

fandom_popularity = [35, 20, 20, 14, 12, 9, 8, 7, 6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4]

delays = [24, 26, 28, 30, 32]
delay = np.random.choice(delays)
block_try_count = 0

url_prefix = "https://archiveofourown.org/tags/"
url_suffix = "/works"

### get stuff
for i, fandom_name in enumerate(fandoms_names) :
    page_counter = np.random.randint(100, 200)
    work_counter = 0
    fandoms_tags_list = []
    print(fandom_name)
    while True :
        print("page", page_counter, "works", work_counter)
        try :
            html = requests.get(url_prefix + fandoms_urls[i] + url_suffix, params = {'page': str(page_counter)})
        except :
            print("blocked")
            time.sleep(200)
            block_try_count += 1
            if block_try_count >= 3 :
                print("give up")
                exit()
            continue
        
        html.encoding = "utf-8-sig"
        soup = BeautifulSoup(html.text, features = "html5lib")
        works = soup.find_all(attrs = {"role" : "article"})
        block_try_count = 0
        
        for work in works : 
            try :
                hits = work.find("dd", attrs = {"class" : "hits"}).string
            except :
                hits = 0
            if int(hits) > HIT_THRESOLD :
                work_counter += 1
                id = work.find("h4").contents[1].attrs["href"][7:]
                rating = work.find(attrs = {"class" : "rating"}).string
                category = work.find(attrs = {"class" : "category"}).string
                tags_list = work.find_all("li", attrs = {"class" : "warnings", "class" : "freeforms"})
                
                tags_set = set()
                tags_set.add(rating.lower())
                tags_set.add(category.lower())
                for tag in tags_list :
                    a = tag.contents[0].string.lower()
                    if len(a) > 1 :
                        tags_set.add(a)
                fandoms_tags_list.append({"fandom" : fandom_name, "tags" : tags_set})
        
        time.sleep(np.random.choice(delays))
        if work_counter < WORKS_NUM :
            page_counter += 1
        else :
            break

    ### preprocess stuff
    # count
    all_tags_counter = {}
    for ft_par in fandoms_tags_list :
        for tag in ft_par["tags"] :
            if not tag in all_tags_counter :
                all_tags_counter[tag] = 1
            else :
                all_tags_counter[tag] += 1
    # know what to remove
    tags_to_remove = []
    for key, value in all_tags_counter.items() :
        if value <= 2 :
            tags_to_remove.append(key)
    # remove        
    for ft_par in fandoms_tags_list : 
        for rtag in tags_to_remove :
            if rtag in ft_par["tags"] :
                ft_par["tags"].remove(rtag)

    archive_df = pd.DataFrame(fandoms_tags_list, columns = ["fandom", "tags"])
    #print(archive_df)
    archive_df.to_csv("test/" + fandom_name + "-raw.csv", index = False)

# end for fandom_list
