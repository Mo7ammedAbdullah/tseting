import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.utils import secure_filename
import tensorflow as tf
from PIL import Image
import numpy as np
import cv2
import database as db

app = Flask(__name__)
@app.after_request
def allow_iframe(response):
    # Remove X-Frame-Options if present
    response.headers.pop('X-Frame-Options', None)
    # Allow framing from Streamlit (example origin). Add other origins if needed.
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' http://localhost:8721"
    return response
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# تحميل النماذج
try:
    brain_tumor_model = tf.keras.models.load_model('BrainTumor10EpochsCategorical.h5')
except Exception as e:
    print(f"خطأ في تحميل نموذج ورم الدماغ: {e}")
    brain_tumor_model = None

try:
    skin_cancer_model = tf.keras.models.load_model('SkinCancerModel.h5')
except Exception as e:
    print(f"خطأ في تحميل نموذج سرطان الجلد: {e}")
    skin_cancer_model = None

try:
    eye_disease_model = tf.keras.models.load_model('EyeDiseaseModel.h5')
except Exception as e:
    print(f"خطأ في تحميل نموذج أمراض العيون: {e}")
    eye_disease_model = None

# دوال تفسير النتائج
def get_brain_tumor_class(classNo):
    return "لا يوجد ورم" if classNo == 0 else "يوجد ورم" if classNo == 1 else "غير معروف"

def get_skin_cancer_class(classNo):
    return "غير سرطاني" if classNo == 0 else "سرطاني" if classNo == 1 else "غير معروف"

def get_eye_disease_class(classNo):
    return "سليم" if classNo == 0 else "اعتلال الشبكية السكري" if classNo == 1 else "غير معروف"

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.check_user(username, password):
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'اسم المستخدم أو كلمة المرور خاطئة'})
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.create_user(username, password):
            session['username'] = username
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'اسم المستخدم موجود بالفعل'})
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    diagnosis_result = None
    records = []

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            patient_name = request.form.get('patient_name')
            patient_gender = request.form.get('patient_gender')
            patient_age = request.form.get('patient_age')
            scan_type = request.form.get('scan_type')
            diagnosis_date = request.form.get('diagnosis_date')
            notes = request.form.get('notes')

            if file.filename == '' or not patient_name or not patient_age or not scan_type or not diagnosis_date:
                diagnosis_result = 'الرجاء ملء جميع الحقول وتحميل صورة.'
            else:
                try:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                    image = cv2.imread(file_path)
                    if image is None:
                        diagnosis_result = 'خطأ: لم يتمكن من قراءة الصورة.'
                    else:
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        image = Image.fromarray(image).resize((64, 64))
                        image = np.array(image) / 255.0
                        input_img = np.expand_dims(image, axis=0)

                        model = None
                        diagnosis_type_name = ''

                        if scan_type == 'brain_tumor' and brain_tumor_model:
                            model = brain_tumor_model
                            diagnosis_type_name = 'ورم الدماغ'
                        elif scan_type == 'skin_cancer' and skin_cancer_model:
                            model = skin_cancer_model
                            diagnosis_type_name = 'سرطان الجلد'
                        elif scan_type == 'eye_disease' and eye_disease_model:
                            model = eye_disease_model
                            diagnosis_type_name = 'أمراض العيون'
                        else:
                            diagnosis_result = f"خطأ: النموذج الخاص بـ {scan_type} غير متوفر."

                        if model:
                            prediction = model.predict(input_img)
                            predicted_class = np.argmax(prediction)

                            if scan_type == 'brain_tumor':
                                class_name = get_brain_tumor_class(predicted_class)
                            elif scan_type == 'skin_cancer':
                                class_name = get_skin_cancer_class(predicted_class)
                            elif scan_type == 'eye_disease':
                                class_name = get_eye_disease_class(predicted_class)

                            # إضافة السجل بدون نسبة الثقة
                            db.add_record(
                                session['username'],
                                patient_name,
                                patient_gender,
                                patient_age,
                                diagnosis_type_name,
                                class_name,
                                diagnosis_date,
                                notes
                            )

                            diagnosis_result = f"الاسم: {patient_name} - العمر: {patient_age} - الجنس: {patient_gender} - التشخيص: {class_name}"

                            os.remove(file_path)
                except Exception as e:
                    print(f"خطأ في التشخيص: {e}")
                    diagnosis_result = f"حدث خطأ أثناء التشخيص. ({e})"

        elif 'search_name' in request.form:
            search_name = request.form.get('search_name')
            records = db.search_records(session['username'], search_name)

    if request.method == 'GET' or 'search_name' not in request.form:
        records = db.get_user_records(session['username'])

    return render_template('dashboard.html',
                           diagnosis_result=diagnosis_result,
                           all_records=records,
                           search_results=None)

if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=8721, debug=False)









