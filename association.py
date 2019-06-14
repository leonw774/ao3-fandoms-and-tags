import os
import sys
import pandas as pd
import itertools
from ast import literal_eval

if len(sys.argv) == 3 :
    minsup = float(sys.argv[1])
    minconf = float(sys.argv[2])
else :
    minsup = 0.02
    minconf = 0.65

# import all data-frame
def get_train_df() :
    dfs = []
    for filename in os.listdir("train/") :
        dfs.append(pd.read_csv("train/" + filename))
    train_df = pd.concat(dfs)
    return train_df

def preprocess_train_df(train_df) :
    data_list = []
    item_dict = {}
    count = 0
    # replace tag strings to numbers
    # cause it will be easier to code
    for index, row in train_df.iterrows() :
        fandom_id = row["fandom"]
        tags_set = literal_eval(row["tags"])
        tags_set.add(fandom_id)
        replaced_tags_set = set()
        for tag in tags_set :
            if not tag in item_dict :
                item_dict[tag] = count
                item_dict[count] = tag
                count += 1
            replaced_tags_set.add(item_dict[tag])
        data_list.append(replaced_tags_set)
    return data_list, item_dict, count

data_list, item_dict, elem_count = preprocess_train_df(get_train_df())
print(len(data_list), len(item_dict) // 2)

def support(item_set) :
    count = 0
    for this_set in data_list :
        if item_set <= this_set :
            count += 1
    return (count / len(data_list))

def confidence(condition, over) :
    count_cond = 0
    count_over = 0
    for this_set in data_list :
        if condition <= this_set :
            count_cond += 1
        if over <= this_set :
            count_over += 1
    if count_cond == 0 :
        return 0
    else :
        return count_over / count_cond

tier = 0
items = set([frozenset([x]) for x in range(elem_count)])
basis_set = list()
freq_item_set = list()
removed_set = set()

freq_item_set.append(items)

# make frequent set
while True :
    print(tier)
    # check sup
    for item_set in freq_item_set[tier] :
        if support(item_set) < minsup :
            removed_set.add(item_set)
    freq_item_set[tier] -= removed_set
    # break if nothing left
    if len(freq_item_set[tier]) == 0 :
        freq_item_set.pop()
        break
    # begin to build next tier
    freq_item_set.append(set())
    basis_set.append(set())
    
    for item_set in freq_item_set[tier] :
        basis_set[tier] = basis_set[tier] | item_set
    
    for c in itertools.combinations(basis_set[tier], tier + 2) :
        c = frozenset(c)
        if not any([x < c for x in removed_set]) :
            freq_item_set[tier + 1].add(c)
    tier += 1

# delete 1-item sets because it can not be rule
freq_item_set = freq_item_set[1:]
rules = dict()

# rule generation
for tier in freq_item_set :
    for item_set in tier :
        ignore_set = set()
        for n in range(len(item_set) - 1, 0, -1) :
            survived = False
            for c in itertools.combinations(item_set, n) :
                c = frozenset(c)
                if not any([c < x for x in ignore_set]) :
                    conf = confidence(c, item_set)
                    #print(c, "/", item_set, ":", conf)
                    if conf < minconf :
                        ignore_set.add(c)
                    else :
                        survived = True
                        #print(c, "/", item_set, ":", conf)
                        rules[c] = item_set - c
            if not survived :
                break

# print rule
file = open("rules.txt", "w+")
file.write("minsup: " + str(minsup) + "\nminconf: " + str(minconf) + "\n")
for key, value in rules.items() :
    rule_string = "("
    for k in key :
        rule_string += (item_dict[k] + ", ")
    rule_string += ")\t-->\t("
    for v in value :
        rule_string += (item_dict[v] + ", ")
    rule_string += ")"
    print(rule_string)
    file.write(rule_string + "\n")
    