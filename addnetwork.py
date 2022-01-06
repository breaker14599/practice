import csv
import json
import sys
from flask import (
    Flask, request
)
from elasticsearch import Elasticsearch
import uuid
import time
import pymongo
from utils.database import DataBase

app = Flask(__name__, template_folder="myapp/templates")
existing_jsondata = {}
GlobalConfig = {}
ConfigGlobal = {}
LOCALHOST = "127.0.0.1"
addnetworks_response = {'result': 'success'}
addnetwork_failure = {'result': 'Network Already Exists'}


def loadOriginalJson(filename):
    with open(filename) as json_file:
        return json.load(json_file)

def validate_ip(s):
    if '/' not in s:
        return False
    parts = s.split('/', 1)
    a=parts[0]

    c=parts[1]
    if len(c)>2:
        return False

    b = a.split('.')
    if len(b) != 4:
        return False
    for m in c:
        if not m.isdigit():
            return False
    for x in b:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def getConfig(filename):
    Config = {}
    with open(filename) as f:
        Config = json.load(f)
    return Config


def insert_to_json(lineitem, data):
    print(lineitem)
    mask = lineitem["ipaddress"].split('/')[1]
    data["network"][mask].append(lineitem)
    data["cidr"][mask].append(lineitem["ipaddress"])
    return data


def csv_dict_reader(file_name, data, ipaddress, status, details):
    es = Elasticsearch(GlobalConfig['EsUrlC1'])
    with open(file_name) as f_object:
        reader = csv.DictReader(f_object, delimiter=',')
        for line in reader:
            ip1 = line[ipaddress]
            m = line[status]
            n = line[details]
            b1 = validate_ip(ip1)

            if b1 == True:
                index = json.dumps(data).find(ip1)
                if index == -1:
                    temp = {'ipaddress': ip1, 'status': m, 'details': n}
                    data = insert_to_json(temp, data)
                    insertToes(es,temp)
                    print (temp)


    return data


def insertToes(es, lineitem):
    doc = {}
    uid= uuid.uuid1()
    doc["network"] = lineitem["ipaddress"].split("/")[0]
    doc["mask"] = lineitem["ipaddress"].split("/")[1]
    doc["network_details"] = lineitem["details"]
    doc["network_critical"] = False
    doc["network_watched"] = False
    doc["network_whitelisted"] = False
    doc["timestamp"] = int(time.time() * 1000)
    doc["network_uuid"] = str(uid)
    doc["score"] = 10
    print(doc["network_uuid"]);
    print(json.dumps(doc))

    es.index(index=GlobalConfig['EsIndexEntityNetworks'], doc_type='doc', id=doc["network_uuid"], body=doc)


@app.route("/importcsv", methods=['POST'])
def importcsv():
    file_data = request.json['file_content']


    demo_json = GlobalConfig["network_info"]

    existing_jsondata = loadOriginalJson(demo_json)
    f = open("tmpfile.csv", "w+")
    f.write(file_data.encode('utf-8').strip())
    f.close()
    existing_jsondata = csv_dict_reader("tmpfile.csv", existing_jsondata, 'IP', "status", "details")
    with open(demo_json, 'w') as fp:
        json.dump(existing_jsondata, fp)
    return "success"


@app.route("/addnetwork", methods=['POST'])
def addnetwork():
    es = Elasticsearch(GlobalConfig['EsUrlC1'])

    ip1 = request.json['ipaddress']
    m = request.json['status']
    n = request.json['details']
    network1 = ip1.split("/")[0]
    mask = ip1.split("/")[1]
    res = es.search(index=GlobalConfig['EsIndexEntityNetworks'], body={"query": {"bool": {
        "must": [
            {
                "match": {
                    "network": network1
                }
            },
            {
                "match": {
                    "mask": mask
                }
            }
        ]
    }
    }})

    c = len(res["hits"]["hits"])
    if c > 0:
        response = json.dumps(addnetwork_failure)

        return response
    temp = {'ipaddress': ip1, 'status': m, 'details': n}

    demo_json = GlobalConfig["network_info"]
    existing_jsondata = loadOriginalJson(demo_json)

    data = insert_to_json(temp, existing_jsondata)
    jsonFile = open(demo_json, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

    insertToes(es, temp)
    response = json.dumps(addnetworks_response)

    return response



if __name__ == '__main__':
    #    main()
    if len(sys.argv) != 2:
        print("Usage: python addnetwork.py <config-name>")
        sys.exit(1)
    ConfigGlobal = getConfig(sys.argv[1:][0])
    GlobalConfig = DataBase(ConfigGlobal).dbquery({}, "global_config")[0]["config"]
    print(GlobalConfig["network_info"])
    app.run(host="0.0.0.0", port="7000")
