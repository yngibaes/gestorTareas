from flask import Flask
from app import db
import datetime

class Tareas():
   id = db.Column(db.Integer, primary_key=True)
   nombreTar = db.Column(db.String(200), nullable=False)
   fechaInicio = db.Column(db.Date, default=datetime.utcnow)
   fechaFin = db.Column(db.Date)
   Estado = db.Column(db.String(200), nullable=False)