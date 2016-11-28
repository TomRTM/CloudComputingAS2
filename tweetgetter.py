
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from shapely.geometry import Polygon
import time
import json
import boto.sqs

access_token='711280829754957824-C9G1QZ59Ukg8aC7fC71RahXKrkaJwhs'
access_token_secret='SzJw81cTi69Ek9ZFAGgcQCIqpcKsXENxXOcUXYRiuYj1h'
consumer_key='FULJuYkzUUQPGBktEpleo1faG'
consumer_secret='LCeH1iDc0W2X4Qjh7Oiz3fqxqkT2yknk4uIO3zwUHudWcoUydY'


sqs = boto.sqs.connect_to_region("us-east-1")
myQueue = sqs.create_queue("cloud_as2")

begtime = time.time()


class MyStreamListener(tweepy.StreamListener):

        def on_status(self, status):
            if status.place:
                author = status.author.name
                text = status.text
                tweetId = status.id
                lt = [tuple(l) for l in status.place.bounding_box.coordinates[0]]
                polygon = Polygon(lt)
                lat = polygon.centroid.y
                lon = polygon.centroid.x
                tweetdict = dict(author=author,status=text,tweetId=tweetId,longitude=lon,latitude=lat)
                tosend = json.dumps(tweetdict)
                sqs.send_message(myQueue, tosend)
                print ('got message!')
            else:
                pass


mysl = MyStreamListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, mysl)
stream.filter(languages=["en"],track=["love","dog","trump","christmas","world"])





