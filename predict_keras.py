import os
import pandas as pd
from ast import literal_eval
'''
from keras import optimizers
from keras.models import Sequential, Model
from keras.layers import Activation, Dense
'''
# add Graphviz path
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

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

# import all data-frame
def get_df(name) :
    dfs = []
    for filename in os.listdir(name + "/") :
        dfs.append(pd.read_csv(name + "/" + filename))
    result_df = pd.concat(dfs)
    result_df.drop(columns = ["id"])
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
            row_dict[tag] = 1
        tag_table.append(row_dict)
    train_df = pd.DataFrame(tag_table).fillna(0)
    
    tag_table = []
    for index, tags in test_df.iteritems():
        tags_set = literal_eval(tags)
        row_dict = {}
        for tag in tags_set :
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
print(train_array.shape, label_array.shape, test_array.shape, answer_array.shape)
#print(train_array[:2])

model = Sequential()
model.add(Dense(units = 128, input_shape = train_array.shape[1:], activation = "relu"))
model.add(Dense(units = 64, activation = "relu"))
model.add(Dense(units = 32, activation = "relu"))
model.add(Dense(units = label_array.shape[1], activation = "softmax"))
opti = optimizers.sgd(lr = 0.1)
model.compile(loss = 'categorical_crossentropy', optimizer = opti, metrics = ['accuracy'])
model.summary()

model.fit(train_array, label_array, epochs = 16, shuffle = True, validation_split = 0.1, batch_size = 16)
model.save("nn_model.h5")

print(model.evaluate(test_array, answer_array))


