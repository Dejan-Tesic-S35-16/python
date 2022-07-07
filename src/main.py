
import re
from types import MethodDescriptorType
from flask import Flask,render_template,request,session
from flask.helpers import url_for
import mysql.connector
from mysql.connector.errors import custom_error_exception
from werkzeug.utils import redirect
app = Flask(__name__)
app.config['SECRET_KEY'] = "RAF2021-2022"
mydb = mysql.connector.connect(
	host="localhost",
	user="root",
	password="", # ako niste nista menjali u phpmyadminu ovo su standardni
    # username i password
	database="vezba" # iz phpmyadmin 
    )
@app.route('/korisnici')

def korisnici():
	cursor = mydb.cursor(prepared=True)
	sql_upit = "SELECT * FROM korisnik"
	cursor.execute(sql_upit)
	rez_upita =cursor.fetchall()
	n = len(rez_upita)
	for i in range(n):
		rez_upita[i] = list(rez_upita[i])
		m = len(rez_upita[i])
		for j in range(m):
			if isinstance(rez_upita[i][j],bytearray):
				rez_upita[i][j] = rez_upita[i][j].decode()

	return render_template("korisnici.html" ,rez = rez_upita)

@app.route('/register',methods=["POST" , "GET"])

def register():
	if request.method == "GET":

		return render_template("registracija.html")
	
	if request.method == "POST":

		username = request.form['username']
		password = request.form['password']
		confirm = request.form['confirm']
		email = request.form['email']
		privilegija = request.form['privilegija']

		cursor = mydb.cursor(prepared=True)
		sql_upit = "SELECT * FROM korisnik WHERE username=?"
		vrednost = (username,)
		cursor.execute(sql_upit,vrednost)
		rez_upita = cursor.fetchone()
		if rez_upita != None:
			return render_template("registracija.html",userneme_greska="Korisnik sa tim username-om vec postoji")
		else:
			if confirm != password:
				return render_template("registracija.html" , pass_greska= "Sifre se ne poklapaju")
			else:
				cursor = mydb.cursor(prepared=True)
				sql_upit = "INSERT INTO korisnik VALUES(null,?,?,?,?)"
				vrednosti = (username,password,email,privilegija)
				cursor.execute(sql_upit,vrednosti)
				mydb.commit()
				return redirect(url_for('korisnici'))

@app.route('/login' , methods=["POST","GET"])

def login():
	if 'ulogovani_username' in session:
		return redirect(url_for('korisnici'))
	if request.method == "GET":
		return render_template("loginovanje.html")
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']

		cursor = mydb.cursor(prepared=True)
		sql_upit = "SELECT * FROM korisnik WHERE username=?"
		vrednost = (username,)
		cursor.execute(sql_upit,vrednost)
		rez_upita = cursor.fetchone()
		if rez_upita == None:
			return render_template("loginovanje.html" , username_greska="Korisnik sa tim username-om ne postoji")
		else:
			if password != rez_upita[2].decode():
				return render_template("loginovanje.html", pass_greska = "Nije dobra sifra")
			else:
				session['ulogovani_username'] = username
				session['tip_korisnika'] = rez_upita[4]
				return redirect(url_for('korisnici'))
			
@app.route('/logout')

def logout():
	if 'ulogovani_username' in session:
		session.pop('ulogovani_username')
		session.pop('tip_korisnika')
		return redirect(url_for('login'))
	else:
		return redirect(url_for('korisnici'))

@app.route('/delete/<id_korisnika>', methods=["POST"])

def delete(id_korisnika):
	cursor = mydb.cursor(prepared=True)
	sql_upit = "DELETE FROM korisnik WHERE id=?"
	vrednost = (id_korisnika,)
	cursor.execute(sql_upit,vrednost)
	mydb.commit()
	return redirect(url_for('korisnici'))

@app.route('/update/<id_korisnika>',methods=["POST","GET"])

def update(id_korisnika):
	if request.method == "GET":
		cursor = mydb.cursor(prepared=True)
		sql_upit = "SELECT * FROM korisnik WHERE id=?"
		vrednost = (id_korisnika,)
		cursor.execute(sql_upit,vrednost)
		rez_upita = cursor.fetchone()
		if rez_upita == None:
			return "<h1>ne postoji korisnik sa tim id-om</h1>"
		else:
			n = len(rez_upita)
			rez = list(rez_upita)
			for i in range(n):
				if isinstance(rez[i],bytearray):
					rez[i] = rez[i].decode()
			return render_template("update.html",podaci=rez)
	if request.method == "POST":
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']

		cursor = mydb.cursor(prepared=True)
		sql_upit = "UPDATE korisnik SET username=?,password=?,email=? WHERE id=?"
		vrednosti = (username,password,email,id_korisnika)
		cursor.execute(sql_upit,vrednosti)
		mydb.commit()
		return redirect(url_for('korisnici'))
		
		
			
app.run(debug=True)
