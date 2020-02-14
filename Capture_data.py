import tweepy
import os,sys
import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

#########read json file
import json
from pprint import pprint
import os

####used to read the user_id in a json file
####it will output a list of id in json file
def read_json_id(path):
    id_list = []
    for filename in os.listdir(path):
        try:
            with open(path+filename) as f:
                data = json.load(f)
                u_id = data[0]["user"]["id"]
                id_list.append(str(u_id))
        except:
            print("can't open file "+filename)
    
    id_list = list(set(id_list))
    return id_list


###used to read the user name in the json file
def read_json_name(path):
    name_list = []
    for filename in os.listdir(path):
        try:
            with open(path+filename) as f:
                data = json.load(f)
                u_name = data[0]["user"]["screen_name"]
                name_list.append(u_name)
        except:
            print("can't open file "+filename)
    
    name_list = list(set(name_list))
    return name_list

consumer_key = 'uM7XQYaG4TRMGvlL25OovD1Sk'
consumer_secret = 'FSQC77iACkPtFDM4uQuTpgC0bL2tFOp4KoF4K6PIFaDomW3Kkn'
access_key =  '1051691439921319936-RqTV8zKPfVDkqSUaJefOLHeQ6tZDC7'
access_secret = '8RdmrUCLyNlfF7vqUM7e4d3z4qDec8Ncj7qomEwpNkqm5'

##this directory is used to store the raw data collect from twitter
##change this directory to match the directory on your local machine
directory = '/data/corruption_tweet_collect_1_15/'

class listener(StreamListener):
    
    def __init__(self): # constructor: set counter to 0, and open a file for writing tweets
        self.counter = 0
        if not os.path.exists(directory+str(time.strftime('%Y%m%d-%H%M%S'))[:8]):
            os.makedirs(directory+str(time.strftime('%Y%m%d-%H%M%S'))[:8])

        self.output = open(directory + str(time.strftime('%Y%m%d-%H%M%S'))[:8] + '/' + time.strftime('%Y%m%d-%H%M%S') + '.json','w')
        #self.output.write('[')
        #self.account = account_name
        
    
    def on_data(self, data):
        print(data)
        self.output.write(data)
        
        self.counter += 1
        
        if(self.counter > 40000):
            self.output.close() # close the previous file
            if not os.path.exists(directory+str(time.strftime('%Y%m%d-%H%M%S'))[:8]):
                os.makedirs(directory+str(time.strftime('%Y%m%d-%H%M%S'))[:8])
            self.output = open(directory + str(time.strftime('%Y%m%d-%H%M%S'))[:8] + '/' + time.strftime('%Y%m%d-%H%M%S') + '.json','w') # open a new one with current timestamp
            self.counter = 0 # reset counter
        else:
            self.output.write('\n') 
            
        return True
    
    def on_error(self, status_code):
        sys.stderr.write('Error: ' + str(status_code) + '\n')
        time.sleep(60)
        return False


if __name__ == '__main__':

    l = listener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    stream = Stream(auth,l)
    api = tweepy.API(auth)
    
    '''
    Use either the method 1 : input the account manually
    or             method 2 : Reading from the json file
    for filtering
    '''
  
    ########################################################method 1
    #########set the tweet account and get the user_id
    
    #tweet_account = input('Please enter the tweet account you want:')
    tweet_account = ['bribery','bribe','corruption','nepotism','collusion','kickback']
    ######the number of tweet account can't excess 100
    #user_id = [user.id_str for user in api.lookup_users(screen_names=tweet_account)]
    #########set the string of the @ and #
    search_set = []
    for t in tweet_account:
        search_set.append(t)
        search_set.append('#'+t)
        search_set.append('@'+t)
    ###########################################################
    
    
    '''
    #########################################################method 2
    ###this path is the directory of the tweet json file
    ###change the path to the directory of local machine where you put the account.json file
    path = './corruption_collect_1_15/'
    tweet_account = read_json_name(path)
    user_id = read_json_id(path)
    
    ###add @ and # to the list
    user_name = []
    for account in tweet_account:
        user_name+=[account,'@'+account,'#'+account]
    print(user_name)
    print(user_id)
    ###########################################################
    '''

    while(1):
        try:
            #######this stream will collect both tweet from disney and the tweet that mention it or @ it
            #stream.filter(follow = user_id,track=user_name, languages=['en'],async=True)
            stream.filter(track=search_set, languages=['en']) #,async=True)
        except:
            continue


