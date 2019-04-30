import numpy as np
import pandas as pd
import os
from ast import literal_eval

dfs = []

# import all data-frame
for filename in os.listdir("train/") :
    dfs.append(pd.read_csv("train/" + filename))

key_word = [
"happy ending",
"bad ending",
"angst",
"fluff",
"humor",
"smut",
"hurt/comfort",
"canon complaint",
"canon divergence",
"time travel",
"modern setting",
"alternate universe",
]

synonyms = {
"au" : "alternate universe",
"a/b/o" : "alpha/beta/omega dynamics",
"abo" : "alpha/beta/omega dynamics"
}

all_tags_counter = {}

for df in dfs :
    fandom_id = df["fandom"][0]
    #print(fandom_id)
    for i, tags in df["tags"].iteritems() :
        # split multi-in-one tags with key_word
        tags_set = literal_eval(tags)
        for key in key_word :
            if not key in tags_set :
                found = False
                for tag in tags_set :
                    if tag.find(key) != -1 :
                        found = True
                        break
                if found :
                    tags_set.add(key)
        # delete multi-in-one tags
        for key in key_word :
            tags_to_rm = []
            for tag in tags_set :
                if tag.find(key) != -1 :
                    tags_to_rm.append(tag)
                    break
            for tag_rm in tags_to_rm :
                tags_set.remove(tag_rm)
        # replace tags with synonyms
        for nym in synonyms.keys() :
            if nym in tags_set :
                tags_set.remove(nym)
                if not synonyms[nym] in tags_set :
                    tags_set.add(synonyms[nym])
                    
        # save preprocessed tags
        df.at[i, "tags"] = str(tags_set)
        
        # record tags occurance
        for tag in tags_set :
            if tag in all_tags_counter :
                if not fandom_id in all_tags_counter[tag] :
                    all_tags_counter[tag].append(fandom_id)
            else :
                all_tags_counter[tag] = list((fandom_id, ))

# delete tags that only appear in one fandom
tags_to_remove = ["other additional tags to be added"]
for df in dfs :
    fandom_id = df["fandom"][0]
    for i, tags in df["tags"].iteritems() :
        tags_set = literal_eval(tags)
        for tag in tags_set :
            if len(all_tags_counter[tag]) <= 1 :
                tags_to_remove.append(tag)

for df in dfs :
    fandom_id = df["fandom"][0]
    for i, tags in df["tags"].iteritems() :
        tags_set = literal_eval(tags)
        for tag_tm in tags_to_remove :
            if tag_tm in tags_set :
                tags_set.remove(tag_tm)
        df.at[i, "tags"] = str(tags_set)
    df.to_csv("preprocessed-train/" + fandom_id + ".csv", index = False)
