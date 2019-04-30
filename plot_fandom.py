import os
import pandas as pd
from ast import literal_eval
from matplotlib import pyplot as plt

dfs = []

# import all data-frame
for filename in os.listdir("train/") :
    dfs.append(pd.read_csv("train/" + filename))

rating_tags = ["not rated", "general audiences", "teen and up audiences", "mature", "explicit"]    

def drawplot(tags_count, id = None, count_rank_min = 20) :
    # plot ratings
    rating_counts = [tags_count[rtag] if rtag in tags_count else 0 for rtag in rating_tags]
    plt.figure(figsize = (10, 6))
    plt.barh(rating_tags, rating_counts, height = 0.66, color = "#9c1111")
    plt.xlabel("counts")
    plt.ylabel("rating")
    plt.subplots_adjust(left = 0.25)
    for i, v in enumerate(rating_counts) :
        plt.text(v + 0.1, i - 0.1, "%d" % v, va = "bottom")
    if id :
        plt.title(id)
        plt.savefig("fig/" + id + "-rating.png")
    else :
        plt.savefig("fig/" + "rating.png")
    plt.close()
    # remove rating tags
    for rtag in rating_tags :
        if rtag in tags_count :
            tags_count.pop(rtag)
    # sort dictionary into list
    sorted_tags_count = sorted(tags_count.items(), key = lambda kv: kv[1])
    if count_rank_min > len(sorted_tags_count) : count_rank_min = len(sorted_tags_count)
    sorted_tag = [tag_count[0] for tag_count in sorted_tags_count[-count_rank_min :]]
    sorted_count = [tag_count[1] for tag_count in sorted_tags_count[-count_rank_min :]]
    # plot tags
    plt.figure(figsize = (10 + (count_rank_min - 20) // 10, 6 + (count_rank_min - 20) // 5))
    plt.barh(sorted_tag, sorted_count, align = "edge", height = 0.4, color = "#9c1111")
    plt.xlabel("counts")
    plt.ylabel("tag")
    plt.subplots_adjust(left = 0.01 + 0.009 * max([len(tag) for tag in sorted_tag]))
    for i, v in enumerate(sorted_count) :
        plt.text(v + 0.05, i - 0.01, "%d" % v, va = "bottom")
    if id :
        plt.title(id)
        plt.savefig("fig/" + id + "-tags.png")
    else :
        plt.savefig("fig/" + "tags.png")
    plt.close()
# end def drawplot

all_tags_count = {}

for df in dfs :
    fandom_id = df["fandom"][0]
    #print(fandom_id)
    fandom_tags_count = {}
    for tags in df["tags"] :
        tags_set = literal_eval(tags)
        for tag in tags_set :
            if tag in fandom_tags_count :
                fandom_tags_count[tag] += 1
            else :
                fandom_tags_count[tag] = 1
            
            if tag in all_tags_count :
                all_tags_count[tag] += 1
            else :
                all_tags_count[tag] = 1
    drawplot(fandom_tags_count, fandom_id)
drawplot(all_tags_count, id = "all", count_rank_min = 50)
