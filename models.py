from flask_sqlalchemy import SQLAlchemy
from app import app
from datetime import datetime
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agenda.sqlite3"
db = SQLAlchemy(app)


#Classe responsável pelo  Cliente.
class Cliente(db.Model):
    __tablename__ = 'clientes'  

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    telefone = db.Column(db.String(50))
    email = db.Column(db.String(50))

    def __init__(self, nome, telefone, email):
        self.nome = nome
        self.telefone = telefone
        self.email = email


#Classe responsável pelo Agendamento.
class Agendamento(db.Model):
    __tablename__ = 'agendamentos' 
    
    id = db.Column(db.Integer, primary_key=True)
    contato = db.Column(db.String(50))
    data_inicio = db.Column(db.DateTime)
    data_termino = db.Column(db.DateTime)
    tipo_atendimento = db.Column(db.String(50))   
    
    #Foreign Key responsável pelo relacionamento com Cliente. 
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)     
    cliente = db.relationship('Cliente', backref=db.backref('agendamentos', lazy=True))

    def __init__(self, contato, data_inicio, data_termino, tipo_atendimento, id_cliente):
        self.contato = contato
        self.data_inicio = data_inicio
        self.data_termino = data_termino
        self.tipo_atendimento = tipo_atendimento
        self.id_cliente = id_cliente
        
        
#Classe responsável pelas configs do whatsapp
#class Config(db.Model):
#       __tablename__ = 'config'
#       mensagem = db.Column(db.String(255))
#       aviso_horas = db.Column(db.integer())
       
