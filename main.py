# project: p4
# submitter: jnovoa
# partner: none
# hours: 20
# source for data: https://www.kaggle.com/code/spscientist/student-performance-in-exams/data
import pandas as pd
from flask import Flask, request, jsonify
import flask
import time
import re
import matplotlib.pyplot as plt
import matplotlib
import io
matplotlib.use('Agg')

app = Flask(__name__)
count = 0
countA = 0 
countB = 0
myDict = {}
df = pd.read_csv("main.csv")

@app.route('/')
def home():
    global count
    # if count is odd and < 10: A
    if count < 10:
        if (count%2):
            with open("index.html") as f:
                html = f.read()
                count += 1
                return html
        # if count is even and < 10: B
        else:
            with open("indexB.html") as f:
                html = f.read()
                count += 1
                return html
    if countA >= countB:
        with open("index.html") as f:
                html = f.read()
                
    else:
        with open("indexB.html") as f:
                html = f.read()
    
    return html

@app.route("/dashboard_1.svg")
def dashboard1():
    y = request.args.get("y", "yaxis")
    if y == "reading":
        fig, ax = plt.subplots(figsize = (3,2))
        ax.scatter(df["writing score"], df["reading score"])
        ax.set_title("writing score vs reading score")
        ax.set_xlabel("writing score")
        ax.set_ylabel("reading score")
        plt.tight_layout()
        f = io.BytesIO() # save file
        fig.savefig(f, format = "svg")
        plt.close(fig)
    else:
        fig, ax = plt.subplots(figsize = (3,2))
        ax.scatter(df["writing score"], df["math score"])
        ax.set_title("writing score vs math score")
        ax.set_xlabel("writing score")
        ax.set_ylabel("math score")
        plt.tight_layout()
        f = io.BytesIO() # save file
        fig.savefig(f, format = "svg")
        plt.close(fig)
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route("/dashboard_2.svg")
def dashboard2():
    fig, ax = plt.subplots(figsize = (5,5))
    # list of math score with and without test prep
    scores_with_prep = []
    scores_without_prep = []
    for index, row in df.iterrows():
        if row["test preparation course"] != "completed":
            scores_without_prep.append(row["math score"])
        else:
            scores_with_prep.append(row["math score"])

    scores_without_prep
    scores_with_prep
    ax.set_title("Math Score: with vs without preparation")
    ax.boxplot(list([scores_without_prep,scores_with_prep]))
    ax.set_xlabel("test preparation course")
    ax.set_ylabel("math score")
    ax.set_xticklabels(["without prep","with prep"])

    plt.tight_layout()
    f = io.BytesIO()
    fig.savefig(f,format = "svg")
    plt.close()
    return flask.Response(f.getvalue(), headers={"Content-Type": "image/svg+xml"})

@app.route('/browse.json')
def browse_json():
    global myDict
    client_ip = request.remote_addr
    list_of_dicts = df.to_dict(orient='records')
    # list of dicts, each idx is a row
    if not client_ip in myDict:
        # add
        myDict[client_ip] = time.time()
        return jsonify(list_of_dicts)
    else:
        # check time
        myTime = time.time()
        if myTime - myDict[client_ip] < 60:
            # go awway
            return flask.Response("<b>go away</b>",
                              status=429,
                              headers={"Retry-After": "60"})
        else:
            myDict[client_ip] = myTime
        return jsonify(list_of_dicts)

@app.route('/visitors.json')
def visitors_json():
    list_ip = []
    for k,v in myDict.items():
        list_ip.append(k)
    return list_ip

@app.route('/browse.html')
def browse():
    # with open("browse.html") as f:
    #     html = f.read()
    # dataframe
    # return html
    df = pd.read_csv("main.csv")
    
    return "<html><head><meta charset = 'UTF-8'><title>browse</title></head><body><h1>browse</h1>{}</body><html>".format(df.to_html())

@app.route('/donate.html')
def donate():
    global countA
    global countB
    letter = request.args.get("from", "letter")
    if count<10:
        if letter == "A":
            countA+=1
        else:
            countB+=1
    with open("donate.html") as f:
        html = f.read()
    return html

@app.route('/email', methods=["POST"])
def email():
    try:
        with open("emails.txt","r") as f:
            num_subscribed = sum(1 for line in f if line.rstrip()) 
            #https://pynative.com/python-count-number-of-lines-in-file/#:~:text=Use%20readlines()%20to%20get%20Line%20Count,-If%20your%20file&text=This%20is%20the%20most%20straightforward,lines%20present%20in%20a%20file.
    except:
        num_subscribed = 0
    email = str(request.data, "utf-8")
    name = r"^\w+"
    at = r"@"
    domain = r"\w+\.(edu|com|net|io|gov)"
    full_regex = f"(({name})({at})({domain}))"
    if len(re.findall(full_regex, email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
            num_subscribed +=1
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify(f"Please enter a valid email, {email} was invalid") # 3

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.