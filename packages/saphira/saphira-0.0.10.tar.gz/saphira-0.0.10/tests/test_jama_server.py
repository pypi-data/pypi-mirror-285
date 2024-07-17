import argparse
from flask import Flask
import json

app = Flask(__name__)
file = 'jama_items.json'

@app.route('/rest/v1/items/<id>', methods=['GET'])
def index(id):
  items = {file}
  with open() as f:
    items = json.loads(f.read())
  return json.dumps(items[str(id)])

@app.route('/rest/v1/items', methods=['GET'])
def get_items():
  items = {}
  with open(file) as f:
    items = json.loads(f.read())
  ret_items = list(items.values())
  ret_val = {
    'meta': {
      'pageInfo': {
        'startIndex': 0,
        'totalResults': len(ret_items)
      }
    },
    'data': ret_items
  }
  return json.dumps(ret_val)

@app.route('/rest/v1/users/', methods=['GET'])
def get_users():
  return json.dumps({ "data" : [ { "lastName" : "Chalana", "avatarUrl" : "avatarUrl", "active" : True, "customData" : [ { "name" : "Akshay Chalana", "value" : "value" }, { "name" : "Akshay Chalana", "value" : "value" } ], "title" : "Mr.", "firstName" : "Akshay", "licenseType" : "NAMED", "uid" : "uid", "phone" : "phone", "location" : "location", "id" : 5, "authenticationType" : { "name" : "name", "id" : 6 }, "email" : "akshay@saphira.ai", "username" : "username" }], "meta" : { "pageInfo" : { "startIndex" : 5, "resultCount" : 5, "totalResults" : 1 }, "status" : "OK", "timestamp" : "2000-01-23T04:56:07.000+00:00" }, "links" : { "key" : { "href" : "href", "type" : "type" } }, "linked" : { "key" : { "key" : "{}" } } })

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--port')
  parser.add_argument('-f', '--file')
  args = parser.parse_args()
  file = args.file or file
  app.run(host='0.0.0.0', port=args.port or 8080, debug=True)