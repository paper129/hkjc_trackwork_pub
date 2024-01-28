import os
import time
from flask import Flask, Response, request, jsonify, json
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from flask_cors import CORS, cross_origin
from werkzeug.exceptions import HTTPException
from datetime import datetime


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.errorhandler(Exception)
def handle_exception(e):
    # replace the body with JSON
    response = json.dumps({
        'success': False,
        'error': 'HKJC Server Error',
        'errMsg': str(e).replace("\n", " "),
        'updatedDt': str(datetime.utcnow()).split(".")[0]
    })
    return response

@app.route('/api/getTrackwork')
@cross_origin()
def getTrackwork():
    race = request.args.get('race')
    date = request.args.get('date')
    web_loc = request.args.get('loc')

    # The following options are required to make headless Chrome
    # work in a Docker container
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("window-size=1024,768")
    chrome_options.add_argument("--no-sandbox")
    browser = webdriver.Chrome(options=chrome_options)


    link = 'https://racing.hkjc.com/racing/information/Chinese/Racing/LocalTrackwork.aspx?RaceDate='+ date +'&Racecourse=' + web_loc + '&RaceNo=' + str(race)
    browser.get(link)
    time.sleep(5)
    html = browser.page_source
    browser.close()
    try:
        trial_r = BeautifulSoup(html, "html.parser")
        trial_table = trial_r.find_all('table', {"class" : "table_bd f_fs13"})

        # 試閘
        trial_df = pd.read_html(trial_table[0].prettify())[0]
        trial_df_json = pd.DataFrame()
        

        for i in range(0, len(trial_df) + 1):
            trackwork_lst = trial_df.index[trial_df['編號'] == i + 1].tolist()
            if len(trackwork_lst) > 0:
                trial_df_json.at[i, 'No'] = trial_df.at[trackwork_lst[0], '編號']
                trial_df_json.at[i, 'horse_name'] = trial_df.at[trackwork_lst[0], '馬名/  練馬師/  6次近績'].split(" ")[0]
                trial_df_json.at[i, 'trainer'] = trial_df.at[trackwork_lst[0], '馬名/  練馬師/  6次近績'].split(" ")[2]

                if not str(trial_df.at[trackwork_lst[0], '試閘']) == 'nan':
                    trial_str = trial_df.at[trackwork_lst[0], '試閘']
                    trial_str_1stgp = trial_str.split("(")[0]
                    trial_loc = trial_str_1stgp.split(" ")[3] + trial_str_1stgp.split(" ")[4]
                    trial_jkc = trial_str.split("(")[1].split(")")[0]
                    trial_df_json.at[i, 'trial'] = trial_loc
                    trial_df_json.at[i, 'trial_jkc'] = trial_jkc
                else:
                    trial_df_json.at[i, 'trial'] = None
                    trial_df_json.at[i, 'trial_jkc'] = None

                if not str(trial_df.at[trackwork_lst[0], '快操']) == 'nan':
                    trackwork_str = trial_df.at[trackwork_lst[0], '快操']
                    trial_df_json.at[i, 'trackwork'] = trackwork_str.split("(")[0].split(" ")[2] + trackwork_str.split("(")[0].split(" ")[3] 
                    trial_df_json.at[i, 'trackwork_jkc'] = trackwork_str.split(") (")[1].split(") ")[0].replace(")", "")
                    
                else:
                    trial_df_json.at[i, 'trackwork'] = None
                    trial_df_json.at[i, 'trackwork_jkc'] = None
            else:
                trial_df_json.at[i, 'No'] = i + 1
                trial_df_json.at[i, 'horse_name'] = 'None'
                trial_df_json.at[i, 'trainer'] = None
                trial_df_json.at[i, 'trial'] = None
                trial_df_json.at[i, 'trial_jkc'] = None
                trial_df_json.at[i, 'trackwork'] = None
                trial_df_json.at[i, 'trackwork_jkc'] = None

        
        if(trial_df_json.at[len(trial_df_json) - 1, 'horse_name'] == 'None'):
            trial_df_json = trial_df_json.drop(len(trial_df_json) - 1)
        return Response(status=200, response=trial_df_json.to_json(index=False, orient='table', force_ascii=False, indent=4), mimetype='application/json')
    except Exception as e:
        err_js = jsonify({'error': 'HKJC Server Error', 'errMsg': str(e) , 'updatedDt': str(datetime.utcnow()).split(".")[0] })
        return Response(status=500, response=err_js, mimetype='application/json')
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
