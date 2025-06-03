from flask import Flask, render_template, request, redirect, url_for, jsonify
from os import path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app import app
from models import *
from sqlalchemy import select

from datetime import datetime, timedelta
import os.path
import whatsapp

@app.route('/')
def main(): 
  return render_template("home.html",is_menu=True)

# Ainda estou definindo o futuro dessa pagina, não sei se irei usar.    
@app.route('/login')
def login():
  return render_template("login.html")

# Pagina incial     
@app.route('/home')
def home():
  return render_template("home.html",is_menu=True)

# Agenda um cliente, registrando esse agendamento no calendario do google(pessoal do dono do negocio) e no BD interno.
@app.route('/cadastra_agendamento', methods=["GET", "POST"])
def cria_agendamento():
    clientelist = Cliente.query.all()

    if request.method == 'POST':
        nome = request.form.get('nome')
        data_atendimento = request.form.get("data")
        tipo_atendimento = request.form.get("tipo_atendimento")

        if tipo_atendimento == "60":
            tipo_atendimento = 60
        elif tipo_atendimento == "90":
            tipo_atendimento = 90
        elif tipo_atendimento == "120":
            tipo_atendimento = 120

        try:
            # Converte a string da data
            data_inicio = datetime.strptime(data_atendimento, "%Y-%m-%dT%H:%M")
            data_termino = data_inicio + timedelta(minutes=tipo_atendimento)

            # Google Calendar - autenticação
            creds = None
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            if os.path.exists("token.json"):
                creds = Credentials.from_authorized_user_file("token.json", SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                    creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

            service = build("calendar", "v3", credentials=creds)

            event = {
                'summary': f'{nome}',
                'location': '',
                'description': f'Atendimento de :',
                'start': {
                    'dateTime': data_inicio.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': data_termino.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'recurrence': ['RRULE:FREQ=DAILY;COUNT=1'],
                'attendees': [
                    {'email': 'ricardoitjvictorino@gmail.com'},
                    {'email': 'ricardoitjvictorino@gmail.com'},
                ]
            }
            # Cria evento no calendário google.
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created (simulado): {event.get('htmlLink')}")
            
            # Insere no DB
            user = db.session.execute(db.select(Cliente).filter_by(nome=nome)).scalar()
            id_cliente = user.id
            agendamento = Agendamento("1", data_inicio, data_termino, tipo_atendimento, id_cliente)
            db.session.add(agendamento)
            db.session.commit()
            db.session.close()

            return redirect(url_for('lista_agendamentos'))

        except HttpError as error:
            print(f"Erro do Google Calendar: {error}")
        except Exception as e:
            print(f"Erro geral ao cadastrar: {e}")

    return render_template("novo_agendamento.html", clientelist=clientelist,is_menu=False)


# Lista todos agendamentos, inclusive os que ja passaram. Filtrando incialmente os que estão prestes a vencer.
@app.route('/agendamentos', methods=['GET', 'POST'])
def lista_agendamentos():
    nome = request.args.get('nome', '')  
    if nome:
         agendamentos_filtrados = Agendamento.query.join(Cliente).filter(Cliente.nome.ilike(f'%{nome}%')).order_by(Agendamento.data_inicio.asc()).all()
    else:
        agora = datetime.now()
        agendamentos_filtrados = Agendamento.query.filter( Agendamento.data_inicio >= agora).order_by(Agendamento.data_inicio.asc()).all()
        
    lista = []
    for ag in agendamentos_filtrados:
        lista.append({
            'id': ag.id,
            'cliente_nome': ag.cliente.nome,
            'data_inicio': ag.data_inicio.strftime('%d/%m/%Y %H:%M'),
            'data_termino': ag.data_termino.strftime('%d/%m/%Y %H:%M'),
            'tipo_atendimento': ag.tipo_atendimento
        })
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(lista) 
    return render_template('agendamentos.html', agendamentos=agendamentos_filtrados,is_menu=False)
       
# Lista todos os clientes cadastrados.    
@app.route('/clientes', methods=['GET', 'POST'])
def lista_clientes():
  filtro_nome = request.args.get('nome', '').strip()
  if filtro_nome:
        filtro = f"%{filtro_nome}%"
        clientes_filtrados = Cliente.query.filter(Cliente.nome.ilike(filtro)).all()
  else:
        clientes_filtrados = Cliente.query.all()
        
  if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        lista = [{'id': c.id, 'nome': c.nome} for c in clientes_filtrados]
        return jsonify(lista)
      
  return render_template('clientes.html', clientes=clientes_filtrados, clientelist=clientes_filtrados)

# Lista os clientes, passando o ID do cliente no formulário.
@app.route('/cliente/<int:cliente_id>', methods=['GET', 'POST'])
def lista_cliente(cliente_id):
  print(cliente_id)
  cliente = Cliente.query.get(cliente_id)
  return render_template('formcliente.html',cliente=cliente,is_menu=False)

# Cadastra cliente.
@app.route('/cadastra_cliente', methods=["GET", "POST"])
def cria_cliente():
        
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')     
        if request.method == 'POST':
               cliente = Cliente(nome,telefone,email)
               db.session.add(cliente)
               db.session.commit()
               db.session.close()
               return redirect(url_for('lista_clientes'))

        return render_template("novo_cliente.html")

# Deleta cliente, rota que irei usar apenas em caso extremo, pois não vejo necessidade de deletar cliente.
@app.route('/delete/<int:cliente_id>',methods=['POST'])
def deleta_cliente(cliente_id): 
    cliente = Cliente.query.get(cliente_id)
    if request.method == 'POST':
      db.session.delete(cliente)
      db.session.commit()
    return redirect('/clientes',is_menu=False)
  
  
# Após a busca de cliente, essa rota é responsável por trazer o form do cliente de acordo com o ID.
@app.route('/update/<int:cliente_id>',methods=['POST','GET'])
def update_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if cliente:        
        cliente.nome = request.form.get('nome')
        cliente.telefone = request.form.get('telefone')
        cliente.email = request.form.get('email')
        db.session.commit()        
    return redirect(url_for('lista_clientes'))
  
# Calendário para facilitar na rotina
@app.route('/calendario')
def calendario():
  return render_template("calendario.html",is_menu=False)


# Config responsável pela configuração do whatzapp e interface.
@app.route('/config')
def config():
  return render_template("configuracoes.html",is_menu=False)


