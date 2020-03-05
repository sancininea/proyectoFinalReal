################################################################
#
# Importar bibliotecas
#
#################################################################
import flask
from flask import Flask, render_template, Markup, request
import os
from shutil import copyfile
import cv2
from photo import takePhoto
from predictor_keras import doPredict

#################################################################
#
# Sistema - Flask call
#
#################################################################
app=Flask(__name__)

#################################################################
#
# Página principal - Carrousel
#
#################################################################
@app.route("/")
def index():
    return render_template("index.html")

#################################################################
#
# A qué famoso te pareces
#
#################################################################
@app.route("/blog")
def blog():
    return render_template("blog.html")

#################################################################
#
# Flappy bird
#
#################################################################
@app.route("/blogtwo")
def blogtwo():
    return render_template("blogTwo.html")

#################################################################
#
# Tax dashboard
#
#################################################################
@app.route("/blogthree")
def blogthree():
    return render_template("blogThree.html")

#################################################################
#
# About
#
#################################################################
@app.route("/about")
def about():
    return render_template("about.html")

#################################################################
#
# Juego Flappy Bird
#
#################################################################
@app.route("/go", methods=['GET', 'POST'])
def go():
    if flask.request.method == 'POST':
        tipo = request.form['FlapHid']
        print(tipo)
        if tipo == 'human':
            os.startfile('flappy.bat')
        else:
            os.startfile('flappy_IA.bat')
    
    return render_template("go.html")

#################################################################
#
# Cámara - A qué famoso te pareces
#
#################################################################
@app.route("/photos", methods=['GET', 'POST'])
def photos():

    famosos_tot = [
        'Alessandra Ambrosio',
        'Alicia Vikander',
        'Amanda Seyfried',
        'Andy Garci­a',
        'Andy Serkis',
        'Adam Sandler',
        'Anna Kendrick',
        'Barbra Streisand',
        'Benedict Cumberbatch',
        'Bette Midler',
        'Breckin Meyer',
        'Britney Spears',
        'Bruno Mars',
        'Cara Delevingne',
        'Dakota Fanning',
        'Dan Aykroyd'
    ]

    famosos = [
        'Andy Garci­a',
        'Andy Serkis',
        'Adam Sandler',
        'Benedict Cumberbatch',
        'Breckin Meyer',
        'Bruno Mars',
        #'Dan Aykroyd'
    ]

    famosos_muj = [
        'Alessandra Ambrosio',
        'Alicia Vikander',
        'Amanda Seyfried',
        'Anna Kendrick',
        'Barbra Streisand',
        #'Bette Midler',
        'Britney Spears',
        #'Cara Delevingne',
        #'Dakota Fanning',
    ]

    os.remove('static/img/saved_img_125.jpg')
    os.remove('static/img/saved_img.jpg')
    takePhoto()
    famoso = doPredict()
    
    return render_template("photo.html", famoso=famoso+1, nombre=famosos[famoso])

#################################################################
#
# Sistema - Main
#
#################################################################
if __name__=="__main__":
    app.run(debug=True)