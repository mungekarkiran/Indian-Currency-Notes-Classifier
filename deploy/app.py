# lib's
from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import time
import os
import cv2
import datetime
from werkzeug.utils import secure_filename

# variable's
connection = sqlite3.connect('Indian_Currency.db', timeout=1, check_same_thread=False)
cursor = connection.cursor()

# create idpass table
try:
    cursor.execute(f'CREATE TABLE IF NOT EXISTS idpass (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL) ')
    connection.commit()
except Exception as e: 
    print('Table idpass is NOT created : \n',e)

# start app
app = Flask(__name__)

# Set the folder where uploaded files will be saved
UPLOAD_FOLDER = os.path.join('static', 'photos') # 'photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# routing
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/mylogin', methods=['GET', 'POST'])
def mylogin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute(f'''SELECT * FROM idpass WHERE email = "{email}" AND pass = "{password}"; ''')
        connection.commit()
        time.sleep(0.5)
        result = cursor.fetchall()
        print('result : ', result)

        if len(result) > 0:
            return render_template('home.html')
        else:
            return '<b>Wrong email, password!</b>'

@app.route('/myreg', methods=['GET', 'POST'])
def myreg():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:            
            cursor.execute(f'''INSERT INTO idpass (email, pass) VALUES ("{email}", "{password}"); ''')
            connection.commit()
            time.sleep(0.5)
            return render_template('index.html')
        except Exception as e:
            print('Reg. Exception : ',e,'\n')
            return render_template('index.html')

@app.route('/generate_id', methods=['GET', 'POST'])
def generate_id():
    if request.method == "POST":
        roll_num = request.form.get("roll_num")
        name = request.form.get("name")
        stud_class = request.form.get("class")
        stud_division = request.form.get("division")

        data_dict = {
            'roll_num': roll_num,
            'name': name,
            'class': stud_class,
            'division': stud_division
        }
        # Convert the dictionary to a string
        data_string = str(data_dict)

        # Check if the 'file' input field is empty
        if 'photo' not in request.files:
            return 'No file part'
        photo = request.files["photo"]

        # Check if the file is empty
        if photo.filename == '':
            return 'No selected file'

        # Check if the file has an allowed extension (e.g., only allow image files)
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Save the file to the specified folder
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(photo_path)
            # return 'File uploaded successfully'
        else:
            return 'Invalid file format'
        
        # Save the photo and generate a QR code
        # photo_path = os.path.join("photos", photo.filename)
        # photo.save(photo_path)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(app.config['QR_FOLDER'], 'id_card.png')
        qr_img.save(qr_path)

        # return redirect(url_for("generate_id"))
        return render_template("id_card.html", data_dict=data_dict, photo_path=photo_path)
    return render_template("generate_id.html")

# Flask route to display the stored QR code data
@app.route('/scan_id')
def display_qr_codes():
    conn = sqlite3.connect('qr_codes.db')
    qr_cursor = conn.cursor()
    qr_cursor.execute('SELECT * FROM qr_codes')
    qr_codes = qr_cursor.fetchall()
    conn.close()

    return render_template('scan_id.html', qr_codes=qr_codes)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True) #debug=True
    # app.run(debug=False,host='0.0.0.0', port=5000)



