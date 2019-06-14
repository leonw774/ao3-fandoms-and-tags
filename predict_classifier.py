import sys
import os
import numpy as np
import pandas as pd
from ast import literal_eval

from sklearn.ensemble import RandomForestClassifier

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

tag_dict = pd.read_csv("tag_dict.csv").columns

# import all data-frame
def get_df(name) :
    dfs = []
    for filename in os.listdir(name + "/") :
        dfs.append(pd.read_csv(name + "/" + filename))
    result_df = pd.concat(dfs)
    return result_df

def preprocess_df(train_df, test_df) :
    label_df = train_df["fandom"]
    train_df = train_df["tags"]
    answer_df = test_df["fandom"]
    test_df = test_df["tags"]
    
    tag_table = []
    for index, tags in train_df.iteritems():
        tags_set = literal_eval(tags)
        row_dict = {}
        for tag in tags_set :
            if tag in tag_dict :
                row_dict[tag] = 1
        tag_table.append(row_dict)
    train_df = pd.DataFrame(tag_table).fillna(0)
    
    tag_table = []
    for index, tags in test_df.iteritems():
        tags_set = literal_eval(tags)
        row_dict = {}
        for tag in tags_set :
            if tag in tag_dict :
                row_dict[tag] = 1
        tag_table.append(row_dict)
    test_df = pd.DataFrame(tag_table).fillna(0)
    
    s = len(train_df)
    onehot = pd.concat([train_df, test_df], sort = False).fillna(0)
    print(onehot.shape)
    onehot = pd.get_dummies(onehot).to_numpy()
    train_array = onehot[:s]
    test_array = onehot[s:]
    
    for i, name in enumerate(fandoms_names) :
        print(name, i)
        label_df.replace(to_replace = name, value = i)
        answer_df.replace(to_replace = name, value = i)
    label_array = label_df.to_numpy()
    answer_array = answer_df.to_numpy()
    return train_array, label_array, test_array, answer_array

train_array, label_array, test_array, answer_array = preprocess_df(get_df("train"), get_df("test"))
shuffle_array = np.random.permutation(train_array.shape[0])
train_array = train_array[shuffle_array]
label_array = label_array[shuffle_array]
shuffle_array = np.random.permutation(test_array.shape[0])
test_array = test_array[shuffle_array]
answer_array = answer_array[shuffle_array]
print(train_array.shape, label_array.shape, test_array.shape, answer_array.shape)
#print(train_array[:10])
#print(label_array[:10])

model = RandomForestClassifier()

model.fit(train_array, label_array)

print(model.score(test_array, answer_array))


