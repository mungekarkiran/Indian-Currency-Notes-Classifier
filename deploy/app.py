# lib's
from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import time
import os
import cv2
import datetime
from werkzeug.utils import secure_filename
from currency_predict import prediction
import pyttsx3
import uuid

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

# Initialize the webcam capture object
cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
        time.sleep(0.3)
        result = cursor.fetchall()
        # print('result : ', result)

        if len(result) > 0:
            return render_template('home.html')
            # return redirect(url_for("home", flag=False))
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

@app.route('/predict_by_image', methods=['GET', 'POST'])
def predict_by_image():
    if request.method == "POST":
        # Check if the 'file' input field is empty
        if 'image' not in request.files:
            return 'No file part'
        
        photo = request.files["image"]

        # Check if the file is empty
        if photo.filename == '':
            return 'No selected file'

        # Check if the file has an allowed extension (e.g., only allow image files)
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Save the file to the specified folder
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
            photo.save(photo_path)
            # print(f"{photo_path} File uploaded successfully")
        else:
            return 'Invalid file format'
        
        class_label, class_likelihood, plot_data, mytext = prediction(photo_path)

        # Initialize the text-to-speech engine
        engine = pyttsx3.init()

        # Speak the mytext
        engine.say(mytext)

        # Wait for the speech to finish
        engine.runAndWait()
        
        # return redirect(url_for("generate_id"))
        return render_template("home.html", flag=True, photo_path=photo_path, class_label=class_label, class_likelihood=class_likelihood, plot_data=plot_data, mytext=mytext)
    return render_template("home.html", flag=False)

# Flask route to display the stored QR code data
@app.route('/predict_by_video')
def predict_by_video():
    return render_template('predict_by_video.html')

@app.route('/capture', methods=['POST'])
def capture():
    if request.method == "POST":
        # Check if the 'file' input field is empty
        if 'image' not in request.files:
            return 'No file part'
        
        photo = request.files['image']

        # Check if the file is empty
        if photo.filename == '':
            return 'No selected file'

        # Check if the file has an allowed extension (e.g., only allow image files)
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Generate a unique filename using UUID
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{str(uuid.uuid4())}.jpg')
            
            # Save the image to the file
            photo.save(photo_path)
        else:
            return 'Invalid file format'

        class_label, class_likelihood, plot_data, mytext = prediction(photo_path)

        # Initialize the text-to-speech engine
        engine = pyttsx3.init()

        # Speak the mytext
        engine.say(mytext)

        # Wait for the speech to finish
        engine.runAndWait()
        
        # return redirect(url_for("home", flag=False))
        # return redirect(url_for("home", flag=True, photo_path=photo_path, class_label=class_label, class_likelihood=class_likelihood, plot_data=plot_data, mytext=mytext))
        # return render_template("home.html", flag=True, photo_path=photo_path, class_label=class_label, class_likelihood=class_likelihood, plot_data=plot_data, mytext=mytext)
    # return render_template('predict_by_video.html')

    #     return f'Image captured and saved as {filename}'
    # else:
    #     return 'Failed to capture an image'

if __name__ == '__main__':
    # if not os.path.exists('captured_images'):
    #     os.makedirs('captured_images')

    # Run the Flask app
    app.run(debug=True) #debug=True
    # app.run(debug=False,host='0.0.0.0', port=5000)



