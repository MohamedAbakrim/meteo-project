from flask import Flask, render_template, url_for, send_file, request
from bson.json_util import dumps
import json
import threading
from pymongo import MongoClient
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import numpy as np
import os
import requests
import datetime


def update_database(): 
    date = str(datetime.datetime.today() - datetime.timedelta(days=1))
    data = requests.get(f"https://public.opendatasoft.com/api/records/1.0/search/?dataset=donnees-synop-essentielles-omm&q=&rows=10000&sort=date&facet=date&facet=nom&facet=temps_present&facet=libgeo&facet=nom_epci&facet=nom_dept&facet=nom_reg&refine.date={date[0:4]}%2F{date[5:7]}%2F{date[8:10]}")
    my_file = json.loads(data.content.decode("utf-8"))
    my_collection = []
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
    count = 0
    for i in my_collection:
        count += 1
    x = db.Synop.count_documents({"date":{"$regex":f"^{date[0:10]}"}})
    if count > 0 and x == 0:
        db.Synop.insert_many(my_collection)
    else:
        pass
    threading.Timer(86400, update_database).start()

update_database()



app = Flask(__name__)


my_folder = os.path.join('static', 'graphs')
app.config['UPLOAD_FOLDER'] = my_folder







@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        station = request.form.get("station").upper()
        date = request.form.get("date")
        check = db.Synop.count_documents({"date":{"$regex":f"^{date}"},"nom":f"{station}"})
        results = db.Synop.find({"date":{"$regex":f"^{date}"}, "nom":f"{station}"}, {"_id":0})
        return render_template("home.html", title="home", check=check, results=results)
    return render_template("home.html")


@app.route("/export", methods=["GET", "POST"])
def export():  
    if request.method == "POST":
        station = request.form.get("station").upper()
        date = request.form.get("date")
        my_list = list(db.Synop.find({"date":{"$regex":f"^{date}"}, "nom":f"{station}"},{"_id":0}))
        my_json = dumps(my_list)
        with open("files/file.json", "w") as f:
            f.write(my_json)
        check = db.Synop.count_documents({"date":{"$regex":f"^{date}"},"nom":f"{station}"})
        return render_template("export.html", check=check, station=station, date=date)
    return render_template("export.html")


@app.route("/graphs", methods=["GET", "POST"])
def graphs():
    hummidite = os.path.join(app.config['UPLOAD_FOLDER'], 'Hummidite.png')
    temperateur = os.path.join(app.config['UPLOAD_FOLDER'], 'Temperateur.png')
    vitesseVent = os.path.join(app.config['UPLOAD_FOLDER'], 'VitesseVent.png')
    if request.method == "POST":
        station = request.form.get("station").upper()
        date = request.form.get("date")
        check = db.Synop.count_documents({"date":{"$regex":f"^{date}"},"nom":f"{station}"})
        my_list1 = db.Synop.find({"date":{"$regex":f"^{date}"}, "nom":f"{station}"},{"_id":0})
        my_list2 = ["Temperateur", "Hummidite", "VitesseVent"]
        for j in range(3):
            x = []
            y = []
            if check == 8:     
                for i in range(8):
                    y.append(my_list1[i][my_list2[j]])
                    x.append(str(my_list1[i]["date"][11:13])+":00")
                np.array(x)
                np.array(y)
                plt.bar(x,y)
                plt.savefig(f'static/graphs/{my_list2[j]}.png')
        return render_template("graphs.html", check=check, station=station, date=date, hummidite=hummidite, temperateur=temperateur, vitesseVent=vitesseVent)
    return render_template("graphs.html")

@app.route("/download")
def download():
    path = "files/file.json"
    return send_file(path, as_attachment=True)

if __name__ == '__main__': 
    app.run(debug=True)