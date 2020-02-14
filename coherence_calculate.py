###calculate the coherence score for the data
import json
import numpy as np
import math
import gzip
import os, sys
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
import re
import collections

def clean(text):
    text = re.sub(r'[^\x00-\x7F]+','', text)
    text = str.replace(text,',',' ')
    text = str.replace(text,"'",' ')
    text = str.replace(text,'"',' ')
    text = str.replace(text,'!',' ')
    text = str.replace(text,'^',' ')
    text = str.replace(text,'(',' ')
    text = str.replace(text,')',' ')
    text = str.replace(text,'%',' ')
    text = str.replace(text,'-',' ')
    text = str.replace(text,'_',' ')
    text = str.replace(text,'|',' ')
    text = str.replace(text,'.',' ')
    text = str.replace(text,':',' ')
    #text = str.replace(text,'@',' ')
    #text = str.replace(text,'#','')
    text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",text).split())

    text = re.sub('\s+', ' ',text).strip()
    text = text.split(' ')
    new_text = []
    for each in text:
        if(str.find(each,'http') != -1):
            continue
        if not each.isalnum():
            continue
        new_text.append(str.lower(each));
    text = ' '.join(new_text)

    return text

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

###########used to read a single zip file, it will return a list of orginal tweet information
def read_data_from_gzip_filter(filename):
    data = []
    target = 0
    count = 0
    with gzip.open(filename, 'rt') as f:
        for index,line in enumerate(f):
            try:
                tweet = json.loads(line)
                for key in ['hiv','outbreak']:
                    for word in tweet['text'].split():
                        if key in word.lower():
                            data.append(tweet)
                            count += 1
                            target = 1
                            break
                    if target == 1:
                        target = 0
                        break
            except Exception as e:
                print(e)
            #if index > 1000000:
            #    break
    print('There are total '+str(count)+' tweets')
    print('Total tweets is '+str(index))
    return data

def read_data_from_gzip(filename):
    data = []
    target = 0
    count = 0
    with gzip.open(filename, 'rt') as f:
        for index,line in enumerate(f):
            try:
                tweet = json.loads(line)
                data.append(tweet)
            except Exception as e:
                print(e)
    return data


def read_json(file):
    data = []
    count = 1
    print('Read '+file)
    try:
        with open(file,'r') as f:
            for index,line in enumerate(f):
                try:
                    if line.strip():
                        text = get_instagram_text(json.loads(line))
                        if type(text) == list:
                            for t in text:
                                data.append(t)
                        else:
                            data.append(text)
                except:
                    print("can't open line "+str(index))
    except Exception as e:
        print(e)
        with open(file,'r',encoding = 'utf-16') as f:
            for index,line in enumerate(f):
                try:
                    if line.strip():
                        text = get_instagram_text(json.loads(line))
                        if type(text) == list:
                            for t in text:
                                data.append(t)
                        else:
                            data.append(text)
                except Exception as e:
                    print(e)
                    print("can't open line "+str(index))
    return data

###########used to go through the folder, and collect the tweet data
###########it will return the list of tweets in all files in the folder
def read_folder(path):
    text_data = []

    for index,filename in enumerate(sorted(os.listdir(path))):
        #if int(filename[:8])>time:
        #    break
        #if index > 10:
        #    continue
        try:
            d = read_json(path+filename)
            text_data += d
        except Exception as e:
            print(e)
            print("Can't open file "+str(filename))
        print('Finish read '+filename)
    return text_data

###########get text from the list file
###########it will collect the text in it
###########remember the text here is the original one without cleaning
###########and also create a dictionary with tweet_id : text
def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_twitter_text(data):
    flattern_data = flatten(data)
    text = data['text']
    for key in flattern_data:
        if key.split('.')[-1] == 'full_text':
            text = flattern_data[key]
    return text  

def get_instagram_text(data):
    try:
        text = data['edge_media_to_caption']['edges'][0]['node']['text']
    except:
        text = ''
    return text

def get_instagram_comments_text(data):
    text_list = []
    try:
        comments_list = data['edge_media_to_comment']['edges']
    except:
        preview_num = 0
        parent_num = 0
        if 'edge_media_to_parent_comment' in data:
            #print('yes parent')
            parent_num = len(data['edge_media_to_parent_comment']['edges'])
        
        if 'edge_media_preview_comment' in data:
            #print('yes preview')
            preview_num = len(data['edge_media_preview_comment']['edges'])
        
        print(parent_num,preview_num)
        if parent_num >= preview_num:
            comments_list = data['edge_media_to_parent_comment']['edges']
        else:
            comments_list = data['edge_media_preview_comment']['edges']
        
    for comment in comments_list:
        text_list.append(comment['node']['text'])
    return text_list

def get_index(index_path):
    index_list = []
    for l in open(index_path):
        index_list.append(l.split())
    return index_list

def calculate_D_both(index,w1,w2):
    count = 0
    for words in index:
        if w1 in set(words) and w2 in set(words):
            count += 1
    return count
    
def calculate_D(index,w1):
    count = 0
    for words in index:
        if w1 in set(words):
            count += 1
    return count

n_word = 20

if __name__ == '__main__':
    ######analyze the data
    command = sys.argv[1:]
    option = command[0]  ##has option "--help", "umass", "uci"
                         ##"vocab" will write the vocabulary list of these data
                         ##"BTM" will run the btm algorithm to generate the result
    
    if len(command) == 1 and option == "--help":
        print("#########################################"+\
              "\nCommand 'coherence_calculate.py umass btm_path index_path k_value' \
              \ncalculate the coherence score for the current k value based on umass \
              \nThen output the coherence score" +\
              "\n#########################################")
        exit(1)
    
    if len(command) >= 3: 
        btm_path = command[1]
        index_path = command[2]
        k_value = command[3]
        
        zw_pt = btm_path + 'k%d.pw_z' %  int(k_value)
        word_dict = {}
        topic_coherence = []
        index_list = get_index(index_path)
        count_topic = 0
        for l in open(zw_pt):
            print('Begin calculate topic '+str(count_topic))
            vs = [float(v) for v in l.split()]
            wvs = zip(range(len(vs)), vs)
            wvs = sorted(wvs, key=lambda d:d[1], reverse=True)
            #tmps = ' '.join(['%s' % voca[w] for w,v in wvs[:10]])
            coherence_value = 0
            for ind,word1 in enumerate(wvs[:n_word]):
                w1 = str(word1[0])
                if str(w1) not in word_dict:
                    word_dict[str(w1)] = calculate_D(index_list,str(w1))
                coherence = 0
                for word2 in wvs[ind:n_word]:
                    w2 = str(word2[0])
                    if str(w2) not in word_dict:
                        word_dict[str(w2)] = calculate_D(index_list,str(w2))

                    if w1 != w2:
                        if str(w1+' '+w2) not in word_dict and str(w2+' '+w1) not in word_dict:
                            word_dict[str(w1+' '+w2)] = calculate_D_both(index_list,str(w1),str(w2))
                        try:
                            both_num = word_dict[str(w1+' '+w2)]
                        except:
                            both_num = word_dict[str(w2+' '+w1)]
                        w1_num = word_dict[str(w1)]
                        w2_num = word_dict[str(w2)]
                        coherence += math.log((both_num+1)/float(w1_num))
                coherence /= 29
                coherence_value += coherence
            topic_coherence.append(coherence_value)
            count_topic += 1
    for index,t in enumerate(topic_coherence):
        print("Topic "+str(index)+": "+str(t))
    print("Coherence score is "+str(sum(topic_coherence)/float(len(topic_coherence))))


