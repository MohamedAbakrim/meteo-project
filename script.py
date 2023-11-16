from pymongo import MongoClient
import json
import requests
import datetime


with open("data2.json", "r") as f:
    my_collection = []
    res = json.loads(f.read())
    for i in res:
        my_data = {}
        my_data["date"] = i["fields"]["date"]
        my_data["nom"] = i["fields"]["nom"]
        try:
            my_data["Temperateur"] = round(i["fields"]["tc"], 2)
        except:
            my_data["Temperateur"] = ""
        try:
            my_data["VitesseVent"] = i["fields"]["ff"]
        except:
            my_data["VitesseVent"] = ""
        try:
            my_data["Hummidite"] = i["fields"]["u"]
        except:
            my_data["Hummidite"] = ""
        my_collection.append(my_data)


conn = MongoClient()

db = conn["projet"]

# db.create_collection("Synop")

# db.Synop.insert_many(my_collection)


date1 = str(datetime.datetime.today() - datetime.timedelta(days=1))

x = db.Synop.aggregate([
    { 
        "$sort" : { "date" : -1 } 
    },
    {
        "$limit" : 1
    }
])
for i in x:
    date2 = i["date"]

date2 = datetime.datetime.strptime(date2[:10], "%Y-%m-%d")
my_collection = []

while str(date2)[:10] != str(date1)[0:10]:
    date2 = date2 + datetime.timedelta(days=1)
    test = str(date2)
    data = requests.get(f"https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&rows=10000&sort=date&facet=date&facet=nom&facet=temps_present&facet=libgeo&facet=nom_epci&facet=nom_dept&facet=nom_reg&refine.date={test[0:4]}%2F{test[5:7]}%2F{test[8:10]}")
    my_file = json.loads(data.content.decode("utf-8"))
    for i in my_file["records"]:
        my_data = {}
        my_data["date"] = i["fields"]["date"]
        my_data["nom"] = i["fields"]["nom"]
        try:
            my_data["Temperateur"] = round(i["fields"]["tc"], 2)
        except:
            my_data["Temperateur"] = ""
        try:
            my_data["ViteeseVent"] = i["fields"]["ff"]
        except:
            my_data["ViteeseVent"] = ""
        try:
            my_data["Hummidite"] = i["fields"]["u"]
        except:
            my_data["Hummidite"] = ""
        my_collection.append(my_data)

db.Synop.insert_many(my_collection)