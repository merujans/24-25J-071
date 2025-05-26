import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
from utils.image_processing import preprocess_image
from utils.model_loader import ModelLoader, BLAST_CLASSES, GRAIN_CLASSES, BLIGHT_CLASSES
import numpy as np
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# Add these configurations after app creation
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
HI_THRESHOLD = 0.8
LO_THRESHOLD = 0.5

WEATHER_API_URL = 'https://goweather.xyz/weather/Colombo'
EXCHANGE_RATE_API_URL = 'https://latest.currency-api.pages.dev/v1/currencies/usd.json'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RiceBlast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_class = db.Column(db.String(50), nullable=False)
    predicted_probability = db.Column(db.Float, nullable=False)

class RiceBlight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_class = db.Column(db.String(50), nullable=False)
    predicted_probability = db.Column(db.Float, nullable=False)

class RiceGrain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_class = db.Column(db.String(50), nullable=False)
    predicted_probability = db.Column(db.Float, nullable=False)

class PriceForecast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forecast_date = db.Column(db.Date, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    fuel_price = db.Column(db.Float, nullable=False)
    gdp = db.Column(db.Float, nullable=False)
    inflation = db.Column(db.Float, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    growth_rate = db.Column(db.Float, nullable=False)
    arable_land = db.Column(db.Float, nullable=False)
    predicted_retail_price = db.Column(db.Float, nullable=False)
    predicted_producer_price = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)

class BlightRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease = db.Column(db.String(100), nullable=False, unique=True)
    cause = db.Column(db.Text, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    rec_high = db.Column(db.Text, nullable=True)
    rec_medium = db.Column(db.Text, nullable=True)
    rec_low = db.Column(db.Text, nullable=True)
    preventive_measures = db.Column(db.Text, nullable=False)

class BlastRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease = db.Column(db.String(100), nullable=False, unique=True)
    cause = db.Column(db.Text, nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    rec_high = db.Column(db.Text, nullable=True)
    rec_medium = db.Column(db.Text, nullable=True)
    rec_low = db.Column(db.Text, nullable=True)
    preventive_measures = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def bucket(prob: float) -> str:
    if prob >= HI_THRESHOLD:
        return "high"
    if prob >= LO_THRESHOLD:
        return "medium"
    return "low"

def _text_from_row(row, prob):
    b = bucket(prob)
    rec = getattr(row, f"rec_{b}") or "-"
    return {
        "bucket": b,
        "recommendations": rec,
        "cause": getattr(row, "cause") or "-",
        "symptoms": getattr(row, "symptoms") or "-",
        "preventive_measures": getattr(row, "preventive_measures") or "-"
    }

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        print(user)
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('auth/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get date 10 days ago
    ten_days_ago = datetime.now() - timedelta(days=365)
    
    # Get recent detections and forecasts
    recent_blasts = RiceBlast.query.filter(RiceBlast.datetime >= ten_days_ago).order_by(RiceBlast.datetime.desc()).limit(10).all()
    recent_blights = RiceBlight.query.filter(RiceBlight.datetime >= ten_days_ago).order_by(RiceBlight.datetime.desc()).limit(10).all()
    recent_grains = RiceGrain.query.filter(RiceGrain.datetime >= ten_days_ago).order_by(RiceGrain.datetime.desc()).limit(10).all()
    recent_forecasts = PriceForecast.query.filter(PriceForecast.datetime >= ten_days_ago).order_by(PriceForecast.datetime.desc()).limit(10).all()
    
    # Get recommendations for blight detections
    blight_recommendations = {}
    for detection in recent_blights:
        row = BlightRecommendation.query.filter_by(disease=detection.predicted_class).first()
        if row:
            blight_recommendations[detection.id] = _text_from_row(row, detection.predicted_probability)

    # Get recommendations for blast detections
    blast_recommendations = {}
    for detection in recent_blasts:
        row = BlastRecommendation.query.filter_by(disease=detection.predicted_class).first()
        if row:
            blast_recommendations[detection.id] = _text_from_row(row, detection.predicted_probability)

    return render_template('dashboard/dashboard.html',
                         recent_blasts=recent_blasts,
                         recent_blights=recent_blights,
                         recent_grains=recent_grains,
                         recent_forecasts=recent_forecasts,
                         blight_recommendations=blight_recommendations,
                         blast_recommendations=blast_recommendations)

@app.route('/rice_blast')
@login_required
def rice_blast():
    detections = RiceBlast.query.order_by(RiceBlast.datetime.desc()).all()
    
    # Create a dictionary of recommendations for non-healthy detections
    recommendations = {}
    for detection in detections:
        row = BlastRecommendation.query.filter_by(disease=detection.predicted_class).first()
        if row:
            recommendations[detection.id] = _text_from_row(row, detection.predicted_probability)

    return render_template('dashboard/rice_blast.html', 
                           detections=detections,
                           recommendations=recommendations)

@app.route('/rice_blast/new', methods=['GET', 'POST'])
@login_required
def new_blast_detection():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image uploaded')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No image selected')
            return redirect(request.url)
        
        if file:
            print('Saving Image')
            # Save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'blast', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            try:
                # Load and preprocess the image
                img_array = preprocess_image(filepath)
                
                # Get prediction
                model = ModelLoader.get_blast_model()
                predictions = model.predict(img_array)
                print(predictions)
                
                # Get the predicted class and probability
                predicted_class_idx = np.argmax(predictions[0])
                predicted_class = BLAST_CLASSES[predicted_class_idx]
                predicted_probability = float(predictions[0][predicted_class_idx])
                
                # Save to database
                detection = RiceBlast(
                    image=os.path.join('uploads', 'blast', filename),
                    title=request.form['title'],
                    predicted_class=predicted_class,
                    predicted_probability=predicted_probability
                )
                db.session.add(detection)
                db.session.commit()
                
                flash('Detection completed successfully')
                print('Detection completed successfully')
                return redirect(url_for('rice_blast'))
                
            except Exception as e:
                print(f'Error during detection: {str(e)}')
                flash(f'Error during detection: {str(e)}')
                return redirect(request.url)
            
    return render_template('dashboard/new_blast_detection.html')

@app.route('/rice_blight')
@login_required
def rice_blight():
    detections = RiceBlight.query.order_by(RiceBlight.datetime.desc()).all()
    
    # Create a dictionary of recommendations for non-healthy detections
    recommendations = {}
    for detection in detections:
        row = BlightRecommendation.query.filter_by(disease=detection.predicted_class).first()
        if row:
            recommendations[detection.id] = _text_from_row(row, detection.predicted_probability)

    print(recommendations)    
    return render_template('dashboard/rice_blight.html', 
                         detections=detections,
                         recommendations=recommendations)

@app.route('/rice_blight/new', methods=['GET', 'POST'])
@login_required
def new_blight_detection():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image uploaded')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No image selected')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'blight', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            try:
                # Load and preprocess the image
                img_array = preprocess_image(filepath)
                
                # Get prediction
                model = ModelLoader.get_blight_model()
                predictions = model.predict(img_array)
                
                # Get the predicted class and probability
                predicted_class_idx = np.argmax(predictions[0])
                predicted_class = BLIGHT_CLASSES[predicted_class_idx]
                predicted_probability = float(predictions[0][predicted_class_idx])
                
                # Save to database
                detection = RiceBlight(
                    image=os.path.join('uploads', 'blight', filename),
                    title=request.form['title'],
                    predicted_class=predicted_class,
                    predicted_probability=predicted_probability
                )
                db.session.add(detection)
                db.session.commit()
                
                flash('Detection completed successfully')
                return redirect(url_for('rice_blight'))
                
            except Exception as e:
                flash(f'Error during detection: {str(e)}')
                return redirect(request.url)
            
    return render_template('dashboard/new_blight_detection.html')

@app.route('/grain_quality')
@login_required
def grain_quality():
    detections = RiceGrain.query.order_by(RiceGrain.datetime.desc()).all()
    return render_template('dashboard/grain_quality.html', detections=detections)

@app.route('/grain_quality/new', methods=['GET', 'POST'])
@login_required
def new_grain_detection():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No image uploaded')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No image selected')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'grain', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            
            try:
                # Load and preprocess the image
                img_array = preprocess_image(filepath)
                
                # Get prediction
                model = ModelLoader.get_grain_model()
                predictions = model.predict(img_array)
                
                # Get the predicted class and probability
                predicted_class_idx = np.argmax(predictions[0])
                predicted_class = GRAIN_CLASSES[predicted_class_idx]
                predicted_probability = float(predictions[0][predicted_class_idx])
                
                # Save to database
                detection = RiceGrain(
                    image=os.path.join('uploads', 'grain', filename),
                    title=request.form['title'],
                    predicted_class=predicted_class,
                    predicted_probability=predicted_probability
                )
                db.session.add(detection)
                db.session.commit()
                
                flash('Detection completed successfully')
                return redirect(url_for('grain_quality'))
                
            except Exception as e:
                flash(f'Error during detection: {str(e)}')
                return redirect(request.url)
            
    return render_template('dashboard/new_grain_detection.html')

@app.route('/price_forecast')
@login_required
def price_forecast():
    forecasts = PriceForecast.query.order_by(PriceForecast.forecast_date.desc()).all()
    return render_template('dashboard/price_forecast.html', forecasts=forecasts)

@app.route('/price_forecast/new', methods=['GET', 'POST'])
@login_required
def new_price_forecast():
    # Get Exchange Rate from API
    response = requests.get(EXCHANGE_RATE_API_URL)
    data = response.json()
    exchange_rate = float(data['usd']['lkr'])

    # Get Temperature from API
    response = requests.get(WEATHER_API_URL)
    data = response.json()
    temperature = data['temperature']

    if request.method == 'POST':
        try:
            # Get form data
            year = int(request.form['year'])
            month = int(request.form['month'])
            forecast_date = date(year, month, 1)
            
            # Validate date
            if forecast_date < date(1996, 1, 1):
                flash('Please select a date after January 1996')
                return redirect(request.url)
            
            # Get other form data
            labour_cost = float(request.form['labour_cost'])
            response = requests.get(EXCHANGE_RATE_API_URL)
            data = response.json()
            exchange_rate = float(request.form['exchange_rate'])
            temperature = request.form['temperature']
            fuel_price = float(request.form['fuel_price'])
            gdp = float(request.form['gdp'])
            inflation = float(request.form['inflation'])
            population = int(request.form['population'])
            growth_rate = float(request.form['growth_rate'])
            arable_land = float(request.form['arable_land'])
            
            # Prepare input data for models
            input_data = np.array([[
                exchange_rate, fuel_price, gdp, inflation,
                population, growth_rate, arable_land
            ]])
            
            # Get predictions
            retail_model = ModelLoader.get_retail_price_model()
            producer_model = ModelLoader.get_producer_price_model()

            print('Loaded Model')
            
            predicted_retail_price = float(retail_model.predict(input_data)[0])
            predicted_producer_price = float(producer_model.predict(input_data)[0])

            print('Got Predictions')
            
            # Save to database
            forecast = PriceForecast(
                forecast_date=forecast_date,
                exchange_rate=exchange_rate,
                fuel_price=fuel_price,
                gdp=gdp,
                inflation=inflation,
                population=population,
                growth_rate=growth_rate,
                arable_land=arable_land,
                temperature=temperature,
                predicted_retail_price=predicted_retail_price,
                predicted_producer_price=predicted_producer_price
            )
            db.session.add(forecast)
            db.session.commit()
            
            flash('Price forecast completed successfully')
            return redirect(url_for('price_forecast'))
            
        except Exception as e:
            flash(f'Error during prediction: {str(e)}')
            print(str(e))
            return redirect(request.url)
            
    return render_template('dashboard/new_price_forecast.html', exchange_rate=exchange_rate, temperature=temperature)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('signup'))

        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully! You can now log in.')
        return redirect(url_for('login'))

    return render_template('auth/signup.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 