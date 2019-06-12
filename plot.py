import os
import pandas as pd
from ast import literal_eval
from matplotlib import pyplot as plt

dfs = []
# import all data-frame
for filename in os.listdir("train/") :
    dfs.append(pd.read_csv("train/" + filename))

rating_tags = ["not rated", "general audiences", "teen and up audiences", "mature", "explicit"]
rating_name = ["not rated", "general", "teen", "mature", "explicit"]

def draw_fandom_plot(tags_count, id, max_rank) :
    # plot ratings
    rating_counts = [tags_count[rtag] if rtag in tags_count else 0 for rtag in rating_tags]
    plt.figure(figsize = (12, 10))
    plt.subplot(2,3,4)
    plt.barh(rating_name, rating_counts, height = 0.4, color = "#9c1111")
    plt.xlabel("counts")
    plt.ylabel("rating")
    #plt.subplots_adjust(left = 0.25)
    for i, v in enumerate(rating_counts) :
        plt.text(v + 1, i - 0.1, "%d" % v, va = "bottom")
    if id :
        plt.title(id)
    # remove rating tags
    for rtag in rating_tags :
        if rtag in tags_count :
            tags_count.pop(rtag)
    # sort dictionary into list
    sorted_tags_count = sorted(tags_count.items(), key = lambda kv: kv[1])
    if max_rank > len(sorted_tags_count) :
        max_rank = len(sorted_tags_count)
    sorted_tag = [tag_count[0] for tag_count in sorted_tags_count[-max_rank :]]
    sorted_count = [tag_count[1] for tag_count in sorted_tags_count[-max_rank :]]
    # plot tags
    plt.subplot(1,2,2)
    plt.barh(sorted_tag, sorted_count, height = 0.4, color = "#9c1111")
    plt.xlabel("counts")
    plt.subplots_adjust(wspace = 0.0125 * max([len(tag) for tag in sorted_tag]))
    for i, v in enumerate(sorted_count) :
        plt.text(v + 0.2, i - 0.2, "%d" % v, va = "bottom")
    if id :
        plt.title(id)
        plt.savefig("fig/fandom/" + id + ".png")
    plt.close()
# end def drawplot

def draw_tag_plot(tag_name, count, fandoms_count) :
    # plot fandoms
    fandom_name = list(fandoms_count.keys())
    counts = list(fandoms_count.values())
    plt.figure(figsize = (6, 5))
    plt.barh(fandom_name, counts, height = 0.5, color = "#9c1111")
    plt.xlabel("counts")
    plt.ylabel("fandom name")
    for i, v in enumerate(counts) :
        plt.text(v + 0.1, i - 0.25, "%d" % v, va = "bottom")
    plt.subplots_adjust(left = 0.3)
    plt.title(tag_name)
    plt.savefig("fig/tag/" + tag_name.replace("/", "-") + "-" + str(count) + ".png")
    plt.close()
# end def draw_tag_plot

all_tags_count = {} # {"tag" : count}
tags_fandoms_count = {} # {"tag" : {"fandom_id" : count}}
fandom_names = []
SHOW_RANK = 30

for df in dfs :
    fandom_id = df["fandom"][0]
    fandom_names.append(fandom_id)
    fandom_tags_count = {}
    for tags in df["tags"] :
        tags_set = literal_eval(tags)
        for tag in tags_set :
            # fandom-tag
            if tag in fandom_tags_count :
                fandom_tags_count[tag] += 1
            else :
                fandom_tags_count[tag] = 1
            # tag-fandom
            if not tag in tags_fandoms_count :
                tags_fandoms_count[tag] = {fandom_id : 1}
            elif not fandom_id in tags_fandoms_count[tag] :
                tags_fandoms_count[tag][fandom_id] = 1
            else :
                tags_fandoms_count[tag][fandom_id] += 1
            # all tags
            if tag in all_tags_count :
                all_tags_count[tag] += 1
            else :
                all_tags_count[tag] = 1
    draw_fandom_plot(fandom_tags_count, fandom_id, max_rank = SHOW_RANK // 2)

draw_fandom_plot(all_tags_count, "all", max_rank = SHOW_RANK)

all_counts = [all_tags_count[key] for key in all_tags_count]
print("all_counts (len:", len(all_counts), ")")

# keep tags with most ocurrence
sorted_tags_count = sorted(all_tags_count.items(), key = lambda kv: kv[1])
sorted_tags = [all_tags_count[0] for all_tags_count in sorted_tags_count[-SHOW_RANK :]]
sorted_tags_fandoms_count = {k : tags_fandoms_count[k] for k in sorted_tags}

for tag_name, fandoms_count in sorted_tags_fandoms_count.items() :
    # check if some fandom is missing
    for fandom_id in fandom_names :
        if not fandom_id in fandoms_count :
            fandoms_count[fandom_id] = 0
    draw_tag_plot(tag_name, all_tags_count[tag_name], fandoms_count)
