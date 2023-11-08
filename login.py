from flask import Flask, request, jsonify, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from PIL import Image, PngImagePlugin
from datetime import datetime

import sqlite3
import os
import logging

# from models import User

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import requests
import io
import json
import sqlite3
import base64
from PIL import Image, PngImagePlugin
from datetime import datetime


app = Flask(__name__)
CORS(app)

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
# Stable Diffusion의 로컬 주소
url = "http://127.0.0.1:7860"
# Stable Diffusion에 적용될 프롬프트
payload = {
    "prompt" : "masterpiece, best quality, highres, ",
    "negative_prompt" : "easynegative"
    }

# 모델 리스트
models = [
    "helloflatcute2d_V10.safetensors [5a7204177d]",
    "pasteldiffusedmix_v22.safetensors [7d21f7acff]",
    "pastelMixStylizedAnime_pastelMixPrunedFP16.safetensors [d01a68ae76]",
    "chosenMix_bakedVae.safetensors [52b8ebbd5b]",
    "v1-5-pruned-emaonly.safetensors [6ce0161689]"
    ]

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "123123123"
db = SQLAlchemy(app)
migrate = Migrate(app, db)

conn.commit()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    birthdate = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if password is None:
            return False
        return check_password_hash(self.password, password)

    def __init__(self, name, birthdate, username, password):
        self.name = name
        self.birthdate = birthdate
        self.username = username
        self.password = generate_password_hash(password)

@app.route('/')
def index():
    return render_template('intro.html')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


with app.app_context():
    db.create_all()

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        name = request.form.get('name')
        birthdate = request.form.get('birthdate')
        username = request.form.get('username')
        password = request.form.get('password')
        print("get 저장")

        # 뉴유저 생성
        new_user = User(name=name, birthdate=birthdate, username=username, password=password)
        print("new 저장")

        # 데베에 뉴유저 추가
        try:
            # 데베에 뉴유저 추가
            db.session.add(new_user)
            db.session.commit()
            flash('Successfully signed up! Please login.', 'success')
            print("데베 저장")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            
            flash('Username already exists. Please choose a different one.', 'error')
            print("Username already exists. Please choose a different one.")
            
            return redirect(url_for('join'))

    return render_template('join.html')
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
            
        # 사용자가 존재하는지 확인
        user = User.query.filter_by(username=username).first()
        if user:                # 비밀번호가 맞는지 확인
            if user.check_password(password):
                session['logged_in'] = True
                session['username'] = username
                session['name'] = user.name
                session['birthdate'] = user.birthdate
                return redirect(url_for('workplace'))
            else:
                # 개발 환경에서만 사용하고 실제 배포 시에는 제거하세요
                # 해시된 비밀번호와 입력된 비밀번호의 해시를 콘솔에 출력
                print(f"Stored hash: {user.password}")
                print(f"Entered hash: {generate_password_hash(password)}")
                flash('Invalid password', 'error')
                print("Incorrect password")
        else:
            flash('Invalid username', 'error')
            print("Username not found")
                
    return render_template('login.html')

# @app.route('/join_success')
# def join_success():
#     if not session.get('logged_in'):
#         return redirect(url_for('login'))
#     else:
#         # 세션에서 username을 가져와서 dashboard.html에 전달합니다.
#         username = session.get('username')
#         return render_template('join_success.html', username=username)
    
@app.route('/workplace')
def workplace():
    if not session.get('logged_in'):
        flash('Please login to view this page.', 'error')
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    global payload
    # payload 초기화
    payload = {
    "prompt" : "",
    "negative_prompt" : "easynegative"
    }
    print(payload)
    return render_template('workplace.html',  username=username)

@app.route('/voice_login_join_choice')
def voice_login_join_choice():
    # Your logic here
    return render_template('voice_login_join_choice.html')

@app.route('/cartoon_gallery1')
def cartoon_gallery1():
    return render_template('cartoon_gallery1.html')

@app.route('/cartoon_gallery2')
def cartoon_gallery2():
    return render_template('cartoon_gallery2.html')

@app.route('/cartoon_gallery3')
def cartoon_gallery3():
    return render_template('cartoon_gallery3.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/live_gallery1')
def live_gallery1():
    return render_template('live_gallery1.html')

@app.route('/live_gallery2')
def live_gallery2():
    return render_template('live_gallery2.html')

@app.route('/live_gallery3')
def live_gallery3():
    return render_template('live_gallery3.html')

@app.route('/my_page')
def my_page():
    if 'username' not in session:
        flash('Please login to view this page.', 'danger')
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    name = session.get('name', 'Guest')
    birthdate = session.get('birthdate', 'Guest')
    
    return render_template('my_page.html', username=username, name = name, birthdate = birthdate)

@app.route('/my_page_my_gallery1')
def my_page_my_gallery1():

    
    return render_template('my_page_my_gallery1.html')

@app.route('/my_page_my_gallery2')
def my_page_my_gallery2():
    return render_template('my_page_my_gallery2.html')

@app.route('/my_page_my_gallery3')
def my_page_my_gallery3():
    return render_template('my_page_my_gallery3.html')

@app.route('/new_back', methods=['GET', 'POST'])
def new_back():
    # payload 값 참조
    global payload

    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json

        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_object')
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_back.html', username=username)

@app.route('/new_complete')
def new_complete():
    username = session.get('username', 'Guest')
    return render_template('new_complete.html', username=username)

@app.route('/new_filter')
def new_filter():
    # payload 값 참조
    global payload

    # 이미지 생성 API 요청
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json = payload)
    print(payload)

    r = response.json()

    # 이미지 저장, 텍스트 데이터를 이진 데이터로 디코딩
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        # API 요청을 보내 이미지 정보 검색
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json = png_payload)
        # PIL 이미지에 메타 데이터 삽입
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        # 현재 날짜와 시간을 문자열로 가져와 파일 이름으로 설정
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f'object/output_t2i{current_time}.png'

        # 이미지 저장
        image.save(file_name, pnginfo = pnginfo)
        
    username = session.get('username', 'Guest')
    return render_template('new_filter.html', username=username)

@app.route('/new_no_save')
def new_no_save():
    username = session.get('username', 'Guest')
    return render_template('new_no_save.html', username=username)

@app.route('/new_object')
def new_object():
    # payload 값 참조
    global payload

    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json

        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')

        # negative_prompt 문자열에 추가
        payload["negative_prompt"] += data.get('negative', '')

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_filter')
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_object.html', username=username)

@app.route('/new_save_success')
def new_save_success():
    username = session.get('username', 'Guest')
    return render_template('new_save_success.html', username=username)

@app.route('/new_shot', methods=['GET', 'POST'])
def new_shot():
    # payload 값 참조
    global payload

    if request.method == 'POST':
        # POST 요청 시 JSON 데이터 파싱
        data = request.json

        # prompt 문자열에 추가
        payload["prompt"] += data.get('prompt', '')

        print("payload 확인:", payload)

        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_back')
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_shot.html', username=username)

@app.route('/new_style', methods=['GET', 'POST'])
def new_style():
    if request.method == 'POST':
        # POST 요청 시 JSON 처리
        data = request.json
        style_number = data['style']
        selected_model = models[style_number - 1]
        option_payload = {
            "sd_model_checkpoint" : selected_model
        }

        # checkpoint 모델 변경
        response = requests.post(url = f'{url}/sdapi/v1/options', json = option_payload)

        # payload 옵션 추가
        options = data.get('options', {})
        if 'styleNumber' in options:
            del options['styleNumber'] #styleNumber 키 제거
        # payload 딕셔너리에 options 값 추가
        for key, value in options.items():
            payload[key] = value
        
        print("payload = ", payload)
        
        # 다음 페이지 리디렉션 url
        redirect_url = url_for('new_shot', _external=True)
        return jsonify(redirect = redirect_url)
    
    else:
        # GET 요청 시 HTML 반환
        username = session.get('username', 'Guest')
        return render_template('new_style.html', username = username)

@app.route('/pastel_gallery1')
def pastel_gallery1():
    return render_template('pastel_gallery1.html')

@app.route('/pastel_gallery2')
def pastel_gallery2():
    return render_template('pastel_gallery2.html')

@app.route('/pastel_gallery3')
def pastel_gallery3():
    return render_template('pastel_gallery3.html')

@app.route('/pro_back')
def pro_back():
    username = session.get('username', 'Guest')
    return render_template('pro_back.html', username=username)

@app.route('/pro_back_complete')
def pro_back_complete():
    username = session.get('username', 'Guest')
    return render_template('pro_back_complete.html', username=username)

@app.route('/pro_complete')
def pro_complete():
    username = session.get('username', 'Guest')
    return render_template('pro_complete.html', username=username)

@app.route('/pro_edit_obj_check')
def pro_edit_obj_check():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_obj_check.html', username=username)

@app.route('/pro_edit_obj_num')
def pro_edit_obj_num():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_obj_num.html', username=username)
@app.route('/pro_edit_object')
def pro_edit_object():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_object.html', username=username)

@app.route('/pro_edit_shot_check')
def pro_edit_shot_check():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_shot_check.html', username=username)

@app.route('/pro_edit_shot_num')
def pro_edit_shot_num():
    username = session.get('username', 'Guest')
    return render_template('pro_edit_shot_num.html', username=username)

@app.route('/pro_filter')
def pro_filter():
    username = session.get('username', 'Guest')
    return render_template('pro_filter.html', username=username)

@app.route('/pro_lora')
def pro_lora():
    username = session.get('username', 'Guest')
    return render_template('pro_lora.html', username=username)

@app.route('/pro_lora_num')
def pro_lora_num():
    username = session.get('username', 'Guest')
    return render_template('pro_lora_num.html', username=username)

@app.route('/pro_more_edit_obj')
def pro_more_edit_obj():
    username = session.get('username', 'Guest')
    return render_template('pro_more_edit_obj.html', username=username)

@app.route('/pro_more_object')
def pro_more_object():
    username = session.get('username', 'Guest')
    return render_template('pro_more_object.html', username=username)

@app.route('/pro_more_specify_obj')
def pro_more_specify_obj():
    username = session.get('username', 'Guest')
    return render_template('pro_more_specify_obj.html', username=username)

@app.route('/pro_no_save')
def pro_no_save():
    username = session.get('username', 'Guest')
    return render_template('pro_no_save.html', username=username)

@app.route('/pro_object')
def pro_object():
    username = session.get('username', 'Guest')
    return render_template('pro_object.html', username=username)

@app.route('/pro_object_complete')
def pro_object_complete():
    username = session.get('username', 'Guest')
    return render_template('pro_object_complete.html', username=username)

@app.route('/pro_save_success')
def pro_save_success():
    username = session.get('username', 'Guest')
    return render_template('pro_save_success.html', username=username)

@app.route('/pro_specify_obj')
def pro_specify_obj():
    username = session.get('username', 'Guest')
    return render_template('pro_specify_obj.html', username=username)

@app.route('/pro_specify_obj_check')
def pro_specify_obj_check():
    username = session.get('username', 'Guest')
    return render_template('pro_specify_obj_check.html', username=username)

@app.route('/pro_specify_obj_check2')
def pro_specify_obj_check2():
    username = session.get('username', 'Guest')
    return render_template('pro_specify_obj_check2.html', username=username)

@app.route('/pro_specify_obj_num')
def pro_specify_obj_num():
    username = session.get('username', 'Guest')
    
    return render_template('pro_specify_obj_num.html', username=username)

@app.route('/pro_specify_obj_num2')
def pro_specify_obj_num2():
    username = session.get('username', 'Guest')
    
    return render_template('pro_specify_obj_num2.html', username=username)

@app.route('/pro_style')
def pro_style():
    username = session.get('username', 'Guest')
    return render_template('pro_style.html', username=username)

@app.route('/voice_join_success')
def voice_join_success():
    return render_template('voice_join_success.html')

@app.route('/voice_join1')
def voice_join1():
    return render_template('voice_join1.html')

@app.route('/voice_join2')
def voice_join2():
    return render_template('voice_join2.html')

@app.route('/voice_login')
def voice_login():
    return render_template('voice_login.html')

@app.route('/watercolor_gallery1')
def watercolor_gallery1():
    return render_template('watercolor_gallery1.html')

@app.route('/watercolor_gallery2')
def watercolor_gallery2():
    return render_template('watercolor_gallery2.html')

@app.route('/watercolor_gallery3')
def watercolor_gallery3():
    return render_template('watercolor_gallery3.html')

@app.route('/whole_gallery1')
def whole_gallery1():
    return render_template('whole_gallery1.html')

@app.route('/whole_gallery2')
def whole_gallery2():
    return render_template('whole_gallery2.html')

@app.route('/whole_gallery3')
def whole_gallery3():
    return render_template('whole_gallery3.html')

@app.route('/intro')
def intro():
 
    return render_template('intro.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        # users = User.query.all()  # 모든 User 레코드를 조회합니다.
        # for user in users:
        #     print(user.id, user.name, user.birthdate, user.username)
        if db.engine.url.drivername == "sqlite":
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
        db.create_all()
        # try:
        #     db.create_all()  # 첫 실행에서만 필요하고 그 다음부터는 주석 처리
        # except Exception as e:
        #     print(f"An error occurred while creating tables: {e}")

    app.run(debug=True)