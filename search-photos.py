import boto3
import json
import urllib3

ES_HOST = 'photos'
REGION = 'us-east-1'
ES_ENDPOINT = 'https://search-photos-ehenwuvn4xngzzrpedw5eni3m4.us-east-1.es.amazonaws.com'

def get_from_open_search(keywords):
    print("start get_from_open_search")
    url = ES_ENDPOINT + '/_search/'
    region = 'us-east-1'

    headers = {'Content-Type': 'application/json'}
    headers.update(urllib3.util.make_headers(basic_auth = 'hw2:123456Hw2!'))

    query = {
        "size": 9,
        "query": {
            "multi_match": {
                "query": keywords
            }
        }
    }
    
    http = urllib3.PoolManager()
    response = http.request('POST', url,
                body = json.dumps(query),
                headers = headers,
                retries = False)
   
    print(response)
    data = json.loads(response.data)
    print(data)
    result = []
    for hit in data['hits']['hits']:
        result.append(hit['_source']['objectKey'])
   
    print("end get_from_open_search")
    print(result)
    return result
    

def lambda_handler(event, context):
    # Define the client to interact with Lex
    client = boto3.client('lex-runtime')
    
    # query = event['query']
    print(event)
    print(f"Query from frontend: {event['queryStringParameters']['q']}")
    # print(event['queryStringParameters']['q'])
    query = event['queryStringParameters']['q']
    
    response = client.post_text(botName='SearchPhotos',
                                botAlias='SearchPhotosLexBot',
                                userId='testuser',
                                inputText=query)
    print(response['slots'])
    keyword_one = response['slots']['KeywordOne']
    keyword_two = response['slots']['KeywordTwo']
    keywords = ""
    if keyword_two != None:
        keywords = keyword_one + keyword_two
    else:
        keywords = keyword_one
    images = get_from_open_search(keywords)
    images = list(set(images))
    resp = {
        'statusCode': 200,
        "headers": {"Access-Control-Allow-Origin":"*", "Content-Type":"application/json"},
        'body': json.dumps({"images": images})
    }
    return  resp
