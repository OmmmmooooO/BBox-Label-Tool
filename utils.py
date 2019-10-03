import json
import os


# Get json label file first key
def get_image_key(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)     
    return list(data.keys())


def get_train_config():
    filename = './train_config.json'
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data
