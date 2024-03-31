from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models import User, Note, Review
from . import db
from datetime import datetime
import sqlite3
from sqlalchemy import desc
from sqlalchemy.sql import func
import random
from sqlalchemy import func

views = Blueprint('views', __name__)

@views.route('/')
def main():
    return render_template('main1.html', user=current_user)

@views.route('/signpage')
def signpage():
    authenticated = current_user.is_authenticated
    return render_template('entry.html', authenticated = authenticated, user = current_user)

@views.route('/profilepage', methods = ['GET', 'POST'])
@login_required
def profilepage():
    top_restaurants = (
        db.session.query(Review.restaurant_name)
        .filter(Review.rating >= 3)  # Рейтинг не менше 3
        .filter(Review.user_id == current_user.id)
        .group_by(Review.restaurant_name)  # Групувати за іменем ресторану
        .order_by(func.max(Review.rating).desc())  # Сортувати за максимальним рейтингом
        .limit(3)  # Обмежити результат до трьох ресторанів
        .all()
    )
    top_restaurants = [restaurant[0] for restaurant in top_restaurants]
    print(top_restaurants)
    restaurant_images = {}
    conn = sqlite3.connect('website/restaurants.db')
    cursor = conn.cursor()
    for restaurant_name in top_restaurants:
        cursor.execute("SELECT image_path FROM restaurants WHERE name = ?", (restaurant_name,))
        result = cursor.fetchone()  # Отримати перший рядок результату
        image_path = result[0]
        restaurant_images[restaurant_name] = image_path

    random_reviews = (
        db.session.query(Review)
        .filter_by(user_id=current_user.id)  # Фільтруємо за ідентифікатором поточного користувача
        .order_by(db.func.random())  # Рандомізуємо порядок записів
        .limit(3)  # Обмежуємо вибірку до трьох випадкових записів
        .all()
    )
    restaurant_reviews={}
    for random_review in random_reviews:
        cursor.execute("SELECT image_path FROM restaurants WHERE name = ?", (random_review.restaurant_name,))
        result = cursor.fetchone()  # Отримати перший рядок результату
        image_path = result[0]
        restaurant_reviews[random_review] = image_path
    return render_template('profile.html', user = current_user, restaurant_images=restaurant_images, restaurant_reviews=restaurant_reviews)



@views.route("/notebutton", methods = ['GET', 'POST'])
def notebutton():
    authenticated = current_user.is_authenticated
    user = User.query.filter_by(id=current_user.id).first()
    if request.method =='POST':
        note = request.form.get('review')
        if len(note)<1:
            flash('Note is too short', category='error')
        else:
            new_note = Note(data=note, user_id=user.id, date=datetime.now())
            print(new_note)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added', category='success')
    return render_template('profile.html', authenticated = authenticated, user = current_user)

@views.route("/restpage/<restaurant_name>")
def restpage(restaurant_name):
    
    connection = sqlite3.connect('website/restaurants.db')
    cursor = connection.cursor()
    cursor.execute("SELECT name, address, rating, tel, time, price, image_path, link FROM restaurants WHERE name=?", (restaurant_name,))
    restaurant = cursor.fetchone()
    connection.close()
    if restaurant:
        # print("Name:", restaurant[0])
        # print("Address:", restaurant[1])
        # print("Rating:", restaurant[2])
        # print("Tel:", restaurant[3])
        # print("Time:", restaurant[4])
        # print("Price:", restaurant[5])
        # print("Image Path:", restaurant[6])
        # print("Link:", restaurant[7])
        views.rest = restaurant[0]
        ratings = (
            db.session.query(Review.rating, func.count())
            .filter(Review.restaurant_name == restaurant_name)
            .group_by(Review.rating)
            .all()
        )
        stars={}
        sum = 0
        for tup in ratings:
            sum+=tup[1]
        for tup in ratings:
            if tup[0]==1:
                stars[1]=round((tup[1]/sum)*100, 1)
            if tup[0]==2:
                stars[2]=round((tup[1]/sum)*100, 1)
            if tup[0]==3:
                stars[3]=round((tup[1]/sum)*100, 1)
            if tup[0]==4:
                stars[4]=round((tup[1]/sum)*100, 1)
            if tup[0]==5:
                stars[5]=round((tup[1]/sum)*100, 1)
        if int('1') not in stars:
            stars[1]=0.0
        if int('2') not in stars:
            stars[2]=0.0
        if int('3') not in stars:
            stars[3]=0.0
        if int('4') not in stars:
            stars[4]=0.0
        if int('5') not in stars:
            stars[5]=0.0
        print(stars)
            
        
        restaurant_reviews = Review.query.filter_by(restaurant_name=views.rest).all()
        return render_template('rest.html', restaurant=restaurant, user = current_user, reviews=restaurant_reviews, stars=stars)
    else:
        return 'Restaurant not found', 404


@views.route("/submit_review", methods=['POST', 'GET'])
# @login_required
def submit_review():
    rating = request.form['rating']
    feedback = request.form['feedback']
    if 'rating' in request.form and 'feedback' in request.form:
        rating = request.form['rating']
        feedback = request.form['feedback']
        print(rating)
        print(feedback)
        review = Review(feedback=feedback, rating=rating, restaurant_name=views.rest, user_id = current_user.id, user_name = current_user.name, image_file = current_user.image_file)
        db.session.add(review)
        db.session.commit()
        return 'Success'
    else:
        flash('Anonymous user', category='error')
        return 'Invalid request parameters', 400
