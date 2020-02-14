#############2018/8/15
#############Jiawei Li
####This file is used to analyze the .json file and capture the words in it

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
                        text = get_twitter_text(json.loads(line))
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
                        text = get_twitter_text(json.loads(line))
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

###########get words from one single clean text, return a list of words
def get_word(text):
    special_word = ['rt','co','amp'] #here is the word we don't want it to show up in the sentence
    words = []
    for w in clean(text).split():
        if isEnglish(w):
            if w not in set(stopwords.words('english')) and w not in special_word:
                words.append(w)
    return words
    

############clean the text data and collect the words, the input should be a list of texts
############it will return a vocabulary of words and a dictionary of frequency
def collect_words(list_text,vocab):
    #words_vocab = []
    for t in list_text:
        vocab += get_word(t)
        vocab = list(set(vocab))
    return vocab

##########write vocab to a txt file
def write_vocab(vocab,vocab_path):
    try:
        file = open(vocab_path, 'w')
        for idx,item in enumerate(vocab):
            #file.write(str(idx)+'\t')
            file.write("%s\n" % item)
        file.close()
    except:
        print("can't open file" + vocab_path)
        
def read_vocab(vocab_path):
    try:
        with open(vocab_path) as f:
            vocab = f.readlines()
            vocab = [x.replace('\n','') for x in vocab] 
            return vocab
    except:
        print("can't open file" + vocab_path)

###########write the index code to the btm index file
def get_index(text_list,vocab):
    index_list = []
    for t in text_list:
        words = get_word(t)
        index = []
        for w in words:
            try:
                index.append(vocab.index(w))
            except Exception as e:
                print(e)
                continue
        index_list.append(index)
    return index_list

def write_index(index_list,output_path):
    #vocab = read_vocab(vocab_path)
    btm_input = open(output_path,'w')
    for i in index_list:
        #words = get_word(t)
        for w in i:
            btm_input.write(str(w)+' ')
        btm_input.write('\n')      
    btm_input.close()
      
    #except:
        #print("can't open file" + vocab_path + " or " +input_path)

######write frequency( dict ) to the json file
def write_freq(freq,freq_path):
    try:
        with open(freq_path, 'w') as fp:
            json.dump(freq, fp)
    except:
        print("can't open file" + freq_path)
    
def run_btm_learning(inputfile, no_topics, vocab_file, alpha, beta, total_number_of_iterations, save_step, output_path):
    # Example:
    # ../../BTM/src/btm est 150 3577 0.3 0.01 1000 10 data_processing_files/btm_input.txt output/BTM_OUTPUT/
    #btm_directory = '../BTM/batch/btm '
    execute_string = btm_directory + 'est ' + str(no_topics) + ' ' +             str(len(open(vocab_file,'r').readlines())) + ' ' +             str(alpha) + ' ' +             str(beta) + ' ' +             str(total_number_of_iterations) + ' ' +             str(save_step) + ' ' +             inputfile + ' ' +             output_path

    print(execute_string)
    os.system(execute_string)

def run_btm_inference(no_topics,inputfile,output_path):
    # Example
    # ../../BTM/src/btm inf sum_b 150 ../data_processing_files/btm_input.txt ../output/BTM_OUTPUT/models/first_run/
    #btm_directory = '../BTM/batch/btm '
    execute_string = btm_directory + 'inf sum_b ' + str(no_topics) + ' ' +             inputfile + ' ' +             output_path

    print(execute_string)
    os.system(execute_string)

#############this is the directory where we store the raw jason file
btm_directory = '../BTM-master/src/btm '

#########parameter
#num_topics = 20
beta = 0.01
total_number_of_iterations = 1000
save_step = 10
read = 0
####
#wenhao_path = '/home/wchen/health/cfar/data/tweets/2014_11.txt.gz' 

if __name__ == '__main__':
    ######analyze the data
    command = sys.argv[1:]
    option = command[0]  ##has option "--help", "vocab", "BTM"
                         ##"vocab" will write the vocabulary list of these data
                         ##"BTM" will run the btm algorithm to generate the result
    
    if len(command) == 1 and option == "--help":
        print("#########################################"+\
              "\nCommand 'analyze_data.py vocab vocab_path index_path json_path ' \
              \nWill write the vocabulary of the json data based on 'json_path' to 'vocab_path' \
              \nThen write index of the text to 'output_path' \
              \nCommand 'analyze_data.py BTM vocab_path index_path btm_path num_topics' \
              \nWill apply BTM to index data in 'input_path' and write result to 'output_path'"+\
              "\n#########################################")
        exit(1)
    
    if len(command) >= 4:
        vocab_path = command[1] 
        index_path = command[2]
        json_path = command[3]  ##path of the folder of json data when option = 'vocab'
                                ##when option == 'BTM' this is the path to the index file

        

        if option == "vocab":
            word_vocab = []
            all_text = []
            index_list = []
            '''
            for index,filename in enumerate(sorted(os.listdir(json_path))):  
                
                if filename == '20190505':
                    read = 1
                if filename == '20190508':
                    read = 0
                if read == 0:
                    continue
                
                print(filename)
                if filename[-5:] == '.json':
                    text_list = read_json(json_path+filename)
                else:
                    json_file = json_path + filename + '/'
                    text_list = read_folder(json_file)

                word_vocab = collect_words(text_list,word_vocab)
            print(len(word_vocab))
            write_vocab(word_vocab,vocab_path)
            '''
            
            
            word_vocab = read_vocab(vocab_path)
            read = 0
            for index,filename in enumerate(sorted(os.listdir(json_path))):
                '''
                if filename == '20190505':
                    read = 1
                if filename == '20190508':
                    read = 0
                if read == 0:
                    continue
                '''
                if filename[-5:] == '.json':
                    text_list = read_json(json_path+filename)
                else:
                    json_file = json_path + filename + '/'
                    text_list = read_folder(json_file)

                index_list += get_index(text_list,word_vocab)
                print('Finish index generation on ' + str(filename))

            print('The total number of text is ' + str(len(index_list)))
            
            write_index(index_list,index_path)
            

    
        ######excute the btm
        if option == "BTM":
            num_topics = command[4]
            alpha = 50/int(num_topics)
            run_btm_learning(index_path, num_topics, vocab_path, alpha, beta, total_number_of_iterations, save_step, json_path)
            run_btm_inference(num_topics,index_path,json_path)

