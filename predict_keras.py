import sys
import os
import numpy as np
import pandas as pd
from ast import literal_eval

from keras import optimizers
from keras.models import Sequential, Model, load_model
from keras.layers import Activation, Dense, BatchNormalization, LeakyReLU
from keras.callbacks import EarlyStopping

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
    onehot = pd.concat([train_df, test_df], sort = False)
    print(onehot.shape)
    onehot = pd.get_dummies(onehot).to_numpy()
    train_array = onehot[:s]
    test_array = onehot[s:]
    
    s = len(label_df)
    onehot = pd.concat([label_df, answer_df], sort = False)
    onehot = pd.get_dummies(onehot).to_numpy()
    label_array = onehot[:s]
    answer_array = onehot[s:]
    return train_array, label_array, test_array, answer_array

train_array, label_array, test_array, answer_array = preprocess_df(get_df("train"), get_df("test"))
shuffle_array = np.random.permutation(train_array.shape[0])
train_array = train_array[shuffle_array]
label_array = label_array[shuffle_array]
shuffle_array = np.random.permutation(test_array.shape[0])
test_array = test_array[shuffle_array]
answer_array = answer_array[shuffle_array]
print(train_array.shape, label_array.shape, test_array.shape, answer_array.shape)
#print(train_array[:2])

if len(sys.argv) == 2 :
    model = load_model(sys.argv[1])
else :
    model = Sequential()
    model.add(Dense(units = 80, input_shape = train_array.shape[1:]))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dense(units = 40))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dense(units = 40))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dense(units = label_array.shape[1], activation = "softmax"))
    opti = optimizers.rmsprop(lr = 0.01, decay = 1e-2)
    model.compile(loss = "categorical_crossentropy", optimizer = opti, metrics = ["accuracy"])
    model.summary()

    model.fit(train_array, label_array, epochs = 16, shuffle = True, validation_split = 0.05, batch_size = 32)
    model.save("nn_model.h5")

print("train acc:", model.evaluate(train_array, label_array))
print("test acc:", model.evaluate(test_array, answer_array))


