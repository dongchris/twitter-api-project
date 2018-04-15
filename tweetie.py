import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items

def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    keys = loadkeys(twitter_auth_filename) 
    consumer_key = keys[0]
    consumer_secret = keys[1]
    access_token = keys[2]
    access_token_secret = keys[3]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    return api

def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    """
    user = api.get_user(name)
    userScreenName = user.screen_name
    userCount = user.statuses_count        
    
    tweetList = []
    for status in tweepy.Cursor(api.user_timeline, id = name).items(100):
      tweetList.append(status)
    
    tweetId = [tweetList[i].id for i in range(len(tweetList))]
    tweetCreated = [tweetList[i].created_at for i in range(len(tweetList))]
    tweetRetweetNum = [tweetList[i].retweet_count for i in range(len(tweetList))]
    tweetText = [tweetList[i].text for i in range(len(tweetList))]
    
    HashTags = []
    tweetHashTags = []
    for j in range(len(tweetList)):      
      for i in range(len(tweetList[j].entities['hashtags'])):
        HashTags.append(tweetList[j].entities['hashtags'][i]['text'])
      tweetHashTags.append(HashTags)
      HashTags = []
    
    Urls = []
    tweetUrls = []
    for j in range(len(tweetList)):      
      for i in range(len(tweetList[j].entities['urls'])):
        Urls.append(tweetList[j].entities['urls'][i]['url'])
      tweetUrls.append(Urls)
      Urls = []

    userMentions = []
    tweetMentions = []
    for j in range(len(tweetList)):
      for i in range(len(tweetList[j].entities['user_mentions'])):
        userMentions.append(tweetList[j].entities['user_mentions'][i]['screen_name'])
      tweetMentions.append(userMentions)
      userMentions = []
    
    analyser = SentimentIntensityAnalyzer()

    tweetScore = [analyser.polarity_scores(tweetText[i])['compound'] for i in range(len(tweetList))]

    tweetDictList = []

    for i in range(len(tweetList)):
      tweetDict = dict()
      tweetDict['id'] = tweetId[i]
      tweetDict['created'] = tweetCreated[i]
      tweetDict['retweeted'] = tweetRetweetNum[i]
      tweetDict['text'] = tweetText[i]
      tweetDict['hashtags'] = tweetHashTags[i]
      tweetDict['urls'] = tweetUrls[i]
      tweetDict['mentions'] = tweetMentions[i]
      tweetDict['score'] = tweetScore [i]
      tweetDictList.append(tweetDict)

    fetchDict = dict()
    fetchDict['user'] = userScreenName
    fetchDict['count'] = userCount
    fetchDict['tweets'] = tweetDictList
    
    return fetchDict

def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image
    """
    
    friendList = []
    
    for friend in tweepy.Cursor(api.friends,screen_name = name).items():
      friendList.append(friend)

    friendId = [friendList[i].id for i in range(len(friendList))]

    userFriendList = []

    for i in range(len(friendId)):
      friendDict = dict()
      user = api.get_user(friendId[i])
      friendDict['name'] = user.name
      friendDict['screen_name'] = user.screen_name
      friendDict['followers'] = user.followers_count
      friendDict['created'] = user.created_at.date()
      friendDict['image'] = user.profile_image_url
      userFriendList.append(friendDict)

    return userFriendList