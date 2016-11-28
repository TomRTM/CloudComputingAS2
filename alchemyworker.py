from multiprocessing import Pool, TimeoutError
import time
import boto.sqs
import ast
import multiprocessing
from alchemyapi_python.alchemyapi import AlchemyAPI
from pyes import *

# AWS Auth
REGION = 'us-east-1'
sqs = boto.sqs.connect_to_region(REGION)
myQueue = sqs.get_queue("cloud_as2")
mysns = boto.sns.connect_to_region(REGION)
topicarn = "arn:aws:sns:us-east-1:315004024184:Topic-ARN"
#mysns.create_topic(topicarn)
global conn
conn = ES('http://search-ccas2-wkp2mz4ca2wjtxn6kvlo6gw6vi.us-east-1.es.amazonaws.com')
# Monkeylearn Auth
alchemyapi = AlchemyAPI()
""

def process_message(tweets_queue, topicarn, alchemy=False):
    """ Reads a message in the queue (long polling), makes a call to alchemy sentiment API and publish the result to
    your SNS topic """

    while 1:
        m = tweets_queue.read()
        if m is not None:
            print(m.get_body())
            message = ast.literal_eval(m.get_body())
            print(message)
            m.delete()
            myText = message["status"]

            #print ("Processing the tweet: ", myText,' \n')
            #Call to the sentiment API
            if alchemy:
                response = alchemyapi.sentiment("text", myText)

                if response["status"] == "OK":
                    test_score = response["docSentiment"]
                    print(test_score)
                    print ("Sentiment: ", response["docSentiment"]["type"], ' \n')
                    result = dict()
                    result["latitude"] = message["latitude"]
                    result["longitude"] = message["longitude"]
                    result["sentiment"] = response["docSentiment"]["type"]
                    result["text"]=message["status"]
                    print(result,'\n')
                    #Publish to the SNS topic
                    publication = mysns.publish(topicarn, result)#有问题，6：1


                    #result=str(result)
                    # longitu=message["longitude"]
                    # latitu=message["latitude"]
                    # text=message["status"]
                    # senti=response["docSentiment"]["type"]
                    # conn.index({'location': {"lat":latitu,"lon":longitu},'message':text,"sentiment":senti},"test-index","test-type")
                    # #lat 1

                    # try:
                    #     conn.indices.delete_index("test-index")
                    # except:
                    #     pass
                    # conn.indices.create_index("test-index")
                   # mapping={"location":{"type":"geo_point"},'message':{'store':'yes','type':'string'},'sentiment':{'type':"string"}}
                   # conn.indices.put_mapping("test-type",{'properties':mapping}, ["test-index"])
            else:
                print (message, ' \n')
        else:
            time.sleep(3)



if __name__ == "__main__":

    processes = 1   # Number of processes to create
    topicarn = "arn:aws:sns:us-east-1:315004024184:Topic-ARN"

    jobs = []
    for i in range(0, processes):
        out_list = list()
        process = multiprocessing.Process(target=process_message, args=(myQueue, topicarn, True))
        jobs.append(process)

    # Start the processes
    for j in jobs:
        j.start()

