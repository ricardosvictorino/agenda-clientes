from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
import os.path
from os import path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES =['https://www.googleapis.com/auth/calendar']


# inicializacao
app = Flask(__name__)
 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agenda.sqlite3"
db = SQLAlchemy(app)

class clientes(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       nome = db.Column(db.String(50))
       telefone = db.Column(db.Integer)
       email = db.Column(db.String(50))

     
       def __init__(self, nome, telefone,email):

              self.nome = nome
              self.telefone = telefone
              self.email = email
              




@app.route('/')
def main(): 
  return render_template("index.html")
     

@app.route('/agendamentos' , methods=["GET", "POST"])
def agendamentos():
  cliente = request.form.get('nome') 
  data =  request.form.get('data')
  clientelist = clientes.query.all() 
  creds = None
  tipo_agendamento = request.form.get('tipo_agendamento')
  whatsapp = request.form.get('whatsapp')
  
  
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  try:
    service = build("calendar", "v3", credentials=creds)
    event = {
              'summary': f'{cliente}',
              'location': '',
              'description': f'Atendimento de :',
              'start': {
              'dateTime': f'{data}:00-03:00',
              'timeZone': 'America/Sao_Paulo',
              },
              'end': {
              'dateTime': f'{data}:00-03:00',
              'timeZone': 'America/Sao_Paulo',
              },
              'recurrence': [
              'RRULE:FREQ=DAILY;COUNT=1'
              ],
              'attendees': [
              {'email': 'ricardoitjvictorino@gmail.com'},
              {'email': 'ricardoitjvictorino@gmail.com'},
              ]

       }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print (f"Event created:  {event.get('htmlLink')}" )

  except HttpError as error:
    print(f"An error occurred: {error}")

  return render_template("agendamentos.html", clientelist=clientelist)
   
     
     
@app.route('/clientes', methods=['GET', 'POST'])
def lista_clientes():
  
       return render_template('clientes.html',clientes=clientes.query.all())

@app.route('/cliente/<int:cliente_id>', methods=['GET', 'POST'])
def lista_cliente(cliente_id):
  cliente = clientes.query.get(cliente_id)
  return render_template('formcliente.html',cliente=cliente)


@app.route('/cadastra_cliente', methods=["GET", "POST"])
def cria_cliente():
        
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        email = request.form.get('email')     
        if request.method == 'POST':
               cliente = clientes(nome,telefone,email)
               db.session.add(cliente)
               db.session.commit()
               db.session.close()
               return redirect(url_for('lista_clientes'))

        return render_template("novo_cliente.html")


@app.route('/delete/<int:cliente_id>',methods=['POST'])
def deleta_cliente(cliente_id): 
    cliente = clientes.query.get(cliente_id)
    if request.method == 'POST':
      db.session.delete(cliente)
      db.session.commit()
    return redirect('/clientes')
  

@app.route('/update/<int:cliente_id>',methods=['POST','GET'])
def update_cliente(cliente_id):
    cliente = clientes.query.get(cliente_id)
    if cliente:        
        cliente.nome = request.form.get('nome')
        cliente.telefone = request.form.get('telefone')
        cliente.email = request.form.get('email')
        db.session.commit()        
    return redirect(url_for('lista_clientes'))




if __name__ == "__main__":
    app.run(debug=True)

