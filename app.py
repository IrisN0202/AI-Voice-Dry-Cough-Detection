from flask import Flask
from flask import request
from flask import render_template,redirect,url_for
import os
from s3 import *
from ProcessAudio import *
app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST":    
        f = request.files['audio_data']
        fname = request.form['fname']
        lname = request.form['lname']
        gender = request.form['gender']
        age = request.form['age']
        dynamoDB = boto3.resource('dynamodb', region_name='ap-southeast-2')
        voiceInfoAWS = dynamoDB.Table("Voicelogs")
        voicelogsItems = voiceInfoAWS.scan()['Items']
        itemCount = len(voicelogsItems)
        voiceID = int(itemCount) + 1
        with open('{}.wav'.format(str(voiceID)), 'wb') as audio:
            f.save(audio)
        print('file uploaded successfully')
        outcome = ProcessAudio('{}.wav'.format(str(voiceID)))
        if 'Coughing' in outcome:
            status = "symptoms found (coughing)"
        else:
            status = "no symptoms identified"
        upload_file('{}.wav'.format(str(voiceID)),'voicefilescovidanalysis','{}.wav'.format(str(voiceID)))
        response = voiceInfoAWS.put_item(
            Item={
                'voiceId': voiceID,
                'age': age,
                'fname': fname,
                'lname': lname,
                'gender': gender,
                'status' : status
                }
            )
        print('rendering template')
        os.remove('{}.wav'.format(str(voiceID)))
        return (str(voiceID))
    else:
        return render_template("index.html")
        
@app.route("/posted", methods=['POST', 'GET'])
def posted():
    id = int(request.args.get('id'))
    dynamoDB = boto3.resource('dynamodb', region_name='ap-southeast-2')
    voiceInfoAWS = dynamoDB.Table("Voicelogs")
    resp = voiceInfoAWS.get_item(
                Key={
                    'voiceId' : id,
                }
            )
    return render_template('posted.html', fname= resp['Item']['fname'], lname= resp['Item']['lname'], gender= resp['Item']['gender'], age= resp['Item']['age'], voiceID= resp['Item']['voiceId'], status = resp['Item']['status'])


@app.route("/history", methods=['POST', 'GET'])
def history():
    dynamoDB = boto3.resource('dynamodb', region_name='ap-southeast-2')
    voiceInfoAWS = dynamoDB.Table("Voicelogs")
    voicelogsItems = voiceInfoAWS.scan()['Items']
    items = []
    for item in voicelogsItems:
        items.append([str(item['voiceId']),str(item['fname']),str(item['lname']),str(item['gender']),str(item['age']),str(item['status'])])
    return render_template('History.html', items = items)


if __name__ == "__main__":
    app.run()