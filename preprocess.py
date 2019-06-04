import numpy as np
import pandas as pd
import os
import re
from ast import literal_eval

dfs = []

# import all data-frame
for filename in os.listdir("raw/") :
    dfs.append(pd.read_csv("raw/" + filename))

key_word = [
"happy ending",
"bad ending",
"angst",
"fluff",
"humor",
"smut",
"hurt/comfort",
"time travel",
]
'''
synonyms = {
"a/b/o" : "alpha/beta/omega dynamics",
"abo" : "alpha/beta/omega dynamics",
"alpha" : "alpha/beta/omega dynamics",
"beta" : "alpha/beta/omega dynamics",
"omega" : "alpha/beta/omega dynamics",
}
'''
all_tags_count = {}
tags_fandoms_counter = {}

for df in dfs :
    fandom_id = df["fandom"][0]
    #print(fandom_id)
    for i, tags in df["tags"].iteritems() :
        try :
            tags_set = literal_eval(tags)
        except :
            print(tags)

        # delete unwanted symbols
        for tag in tags_set :
            tag = re.sub(r"[\?\!\.\,]", "", tag)

        # extract key_word from sub tags
        # and delete key_word divergent tags
        tags_to_add = []
        tags_to_remove = []
        for tag in tags_set :
            found_key = False
            for key in key_word :
                if tag.find(key) != -1 :
                    tags_to_add.append(key)
                    found_key = True
            if found_key :
                tags_to_remove.append(tag)
        for tag_add in tags_to_add :
            tags_set.add(tag_add)
        for tag_rm in tags_to_remove :
            tags_set.remove(tag_rm)
        '''
        # replace tags with synonyms
        for nym in synonyms.keys() :
            if nym in tags_set :
                tags_set.remove(nym)
                if not synonyms[nym] in tags_set :
                    tags_set.add(synonyms[nym])
        '''
        # save preprocessed tags
        df.at[i, "tags"] = str(tags_set)
        
        for tag in tags_set :
            # record tags occurance in fandom
            if tag in tags_fandoms_counter :
                if not fandom_id in tags_fandoms_counter[tag] :
                    tags_fandoms_counter[tag].append(fandom_id)
            else :
                tags_fandoms_counter[tag] = list((fandom_id, ))
                
            # record tags total occurance count
            if tag in all_tags_count :
                all_tags_count[tag] += 1
            else :
                all_tags_count[tag] = 1

# decide min_remove_count
counts = [all_tags_count[key] for key in all_tags_count]
min_remove_count = int(np.mean(counts) + 1)

print("before tags count:", len(counts))
print("max count:", max(counts))
print("min_remove_count", min_remove_count)

tags_to_remove = ["other additional tags to be added"]
for df in dfs :
    fandom_id = df["fandom"][0]
    for i, tags in df["tags"].iteritems() :
        tags_set = literal_eval(tags)
        for tag in tags_set :
            if not tag in tags_to_remove :
                # delete tags that only appear in ONE fandom
                if len(tags_fandoms_counter[tag]) <= 1 :
                    tags_to_remove.append(tag)
                # delete tags that appear less than min
                if all_tags_count[tag] < min_remove_count :
                    tags_to_remove.append(tag)

for df in dfs :
    fandom_id = df["fandom"][0]
    for i, tags in df["tags"].iteritems() :
        tags_set = literal_eval(tags)
        for tag_tm in tags_to_remove :
            if tag_tm in tags_set :
                tags_set.remove(tag_tm)
        df.at[i, "tags"] = str(tags_set)
    df.to_csv("train/" + fandom_id + ".csv", index = False)

# replace tag strings to numbers
# cause it will be easier to code
tag_dict = {}
count = 0
for df in dfs :
    for i, tags in df["tags"].iteritems() :
        tags_set = literal_eval(tags)
        for tag in tags_set :
            if not tag in tag_dict :
                tag_dict[tag] = count
                count += 1
print("after tags count:", count)
dict_df = pd.DataFrame([tag_dict])
dict_df .to_csv("tag_dict.csv", index = False)
