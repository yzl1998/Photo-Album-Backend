import json
import boto3
import os
import sys
import uuid
from botocore.vendored import requests
from datetime import *
import urllib3


REGION = 'us-east-1'
es_endpoint = 'https://search-photos-ehenwuvn4xngzzrpedw5eni3m4.us-east-1.es.amazonaws.com'
es_index = 'photos'
es_type = 'Photo'

def lambda_handler(event, context):
    print(event)
    rekognition_client = boto3.client('rekognition', region_name='us-east-1')
    s3 = boto3.client('s3')

    # comment
    for rec in event['Records']:

        json_data = {}
        name = rec['s3']['bucket']['name']
        key = rec['s3']['object']['key']

        obj = s3.get_object(Bucket=name, Key=key)
        print(obj)
        try:
            print(obj['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'])
            c_label = obj['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
            json_data['x-amz-meta-customlabels'] = c_label
        except:
            print("no custom labels")


        rekognition_response = rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': name,
                    'Name': key,
                },
            },
            MaxLabels=123,
            MinConfidence=70,
        )


        if rekognition_response is not None:
            json_data['objectKey'] = key
            id = json_data['objectKey']
            json_data["bucket"] = name
            json_data["createdTimestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            json_data["labels"] = []
            labels = rekognition_response['Labels']
            print(labels)
            for label in labels:
                json_data["labels"].append(label['Name'])
            print('Json Object is:')
            print("{}".format(json_data))


            json_data = json.dumps(json_data)
            url = es_endpoint + '/' + es_index + '/' + es_type + '/'
            #url = es_endpoint
            print("POST url is:", url)

            headers = {'Content-Type': 'application/json'}
            headers.update(urllib3.util.make_headers(basic_auth = 'hw2:123456Hw2!'))

            http = urllib3.PoolManager()
            response = http.request('POST', url,
                        body = json_data,
                        headers = headers,
                        retries = False)

            print("response form ES is:")
            print(response)

            data = json.loads(response.data)
            print(data)



    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            'Content-Type': 'application/json'
        },
        'body': json.dumps("Image labels have been successfully detected!")
    }
