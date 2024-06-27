from flask import Flask, render_template, request, redirect, url_for, session, Response
from test import change_num, creation_test, df_show
from model_2 import prepro_img, letter_pred
from PIL import Image

import pandas as pd
import os 

app = Flask(__name__, static_url_path='/static')
app.secret_key = "12345"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dev_df', methods = ['GET', 'POST'])
def dev_df():
    if request.method == 'POST':
        num_q = int(request.form.get('numQuestions'))
        num_o = int(request.form.get('numOptions'))
        options = change_num(number_options= num_o, number_questions=num_q)
        # df = creation_test(number_questions=num_q, number_options=num_o, options=options)
        print(num_o)
        df = df_show(num_options=num_o)
        print(df)
        session['df'] = df.to_html()
        session['num_q'] = num_q
        session['num_o'] = num_o
        session['options'] = options
        
        # print(num_o, num_q)
        return redirect(url_for('dev_df'))
    else:  
        df_html = session.get('df', "")
        num_q = session.get('num_q', 0)
        num_o = session.get('num_o', 0)
        options = session.get('options', [])
    return render_template('dev_df.html', df_html=df_html, num_q=num_q, num_o=num_o, options=options)


@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    answers = {}
    num_q = session.get('num_q', 0)
    for i in range(num_q):
        answers[f'question_{i}'] = request.form.get(f'question_{i}')
    print(answers)
    return redirect(url_for('take'))



@app.route('/take', methods=['GET', 'POST'])
def take():
    df_html = session.get('df', None)
    return render_template('take.html', df_html=df_html)


# Función para descargar el archivo CSV
@app.route('/download_csv')
def download_csv():
    df = pd.read_csv('./df.csv')  # Asegúrate de ajustar la ruta según tu caso
    csv = df.to_csv(index=False)

    # Configura la respuesta para descargar el archivo
    response = Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=df.csv"}
    )
    return response

# Ruta para cargar la página de predicción
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        # Verificar si se ha enviado un archivo
        if 'imageFile' not in request.files:
            return redirect(request.url)

        file = request.files['imageFile']

        # Verificar si se ha seleccionado un archivo
        if file.filename == '':
            return redirect(request.url)

        upload_folder = './static/uploads'       
        file_path = os.path.join(upload_folder, file.filename)
    
        file_path = file_path.replace('\\', '/')
        file.save(file_path)


        upload_folder_2 = '/uploads'       
        file_path_2 = os.path.join(upload_folder_2, file.filename)
        file_path_2 = file_path_2.replace('\\', '/')    

        gray, img = prepro_img(file_path)
        gray = Image.fromarray(img)
        gray.save(file_path)

        answer = letter_pred(img, gray)


        # Procesamiento adicional con la imagen, por ejemplo, mostrarla en la página de resultado
        return render_template('prediction_result.html', image_path=file_path_2, answer=answer)

    return render_template('prediction.html')



if __name__ == '__main__':
    app.run(debug = True)