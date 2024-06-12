from flask import Flask, render_template, request, redirect, url_for, session
from dataframe import change_num, creation_test
import pandas as pd
import os 

app = Flask(__name__)
app.secret_key = "12345"


@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        num_q = int(request.form.get('numQuestions'))
        num_o = int(request.form.get('numOptions'))
        options = change_num(number_options= num_o, number_questions=num_q)
        df = creation_test(number_questions=num_q, number_options=num_o, options=options)
        session['df'] = df.to_html()
    else:
        session['df'] = ""
        
    return render_template('home.html', df_html=session['df'])


@app.route('/take')
def take():
    df_html = session.get('df', None)
    return render_template('take.html', df_html=df_html, df=pd.DataFrame())

if __name__ == '__main__':
    app.run(debug = True)


