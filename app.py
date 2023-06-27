import re
import pandas as pd
import sqlite3

from flask import Flask, jsonify, request
from data_cleansing import processing_text

from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

from data_reading_and_writing import create_table, insert_to_table, read_table

# create flask object
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

title = str(LazyString(lambda: 'API Documentation for Data Processing dan Modelling'))
version = str(LazyString(lambda: '1.0.0'))
description = str(LazyString(lambda : 'Dokumnetasi API untuk Data Processing dan Modelling'))
host = LazyString(lambda: request.host)

# create swagger_template
swagger_template = {'info':{'title': title,
                            'version': version,
                            'description': description 
                            },
                    'host': host
                    }

swagger_config = {
    "headers": [],
    "specs": [{"endpoint":"docs", "route": '/docs.json'}],
    "static_url_path": "/flasgger_static",
    "swagger_ui":True,
    "specs_route":"/docs/"
}

swagger = Swagger(app,
                  # template = swagger_template,
                  config = swagger_config
                 )

TABLE_NAME = "tweet_cleaning"


@swag_from("docs/input_processing.yml", methods=['POST'])
@app.route('/input-processing',methods=['POST'])
def input_processing():
    text = request.form.get('text')
    cleaned_tweet = processing_text(text)
    results = read_table(table_name=TABLE_NAME)
    last_index = len(results)
    insert_to_table(value_1=last_index, 
                    value_2=cleaned_tweet, 
                    table_name=TABLE_NAME)
    
    response_data = jsonify({"response":"SUCCESS"})
    return response_data


@swag_from("docs/file_processing.yml", methods=['POST'])
@app.route('/file-processing',methods=['POST'])
def file_processing():
    """
        Memproses file yang akan di upload di swagger_ui atau di HTML.
    """
    # 1 method untuk upload file
    # df = pd.read_csv('data/data.csv', encoding='latin1') # baca datanya
    create_table() # create tablenya
    df = request.form.get('upload_file')
    print(df)
    df = pd.read_csv(df)
    # iterasi untuk setiap tweet yang ada di kolom tweet yang ada di dataframe 'DF'
    for idx, tweet in enumerate(df['Tweet']):
        cleaned_tweet = processing_text(tweet) # process tweetnya
        insert_to_table(value_1=idx, 
                        value_2=cleaned_tweet, 
                        table_name=TABLE_NAME) # insert to table tweet yang sudah di cleaned.
    
    response_data = jsonify({"response":"SUCCESS"}) # karena kita ga butuh response apa2 dari proses ini, selama tidak ada error, return "SUCCESS"
    return response_data

@swag_from("docs/read_index_data.yml", methods=['POST'])
@app.route('/read-index-data',methods=['POST'])
def read_index_data():
    index = request.form.get('index')
    result = read_table(target_index=int(index),
                         table_name=TABLE_NAME)
    response_data = jsonify({"tweets":result})
    return response_data


if __name__ == '__main__':
    app.run(debug=True)
