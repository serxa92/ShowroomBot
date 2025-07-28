from flask import Flask, request, jsonify

app = Flask('')

@app.route('/')
def home():
    return "El bot está vivo y funcionando."

@app.route('/terms')
def terms():
    return '''
    <h1>Términos de Servicio</h1>
    <p>Este bot se ofrece tal cual, sin garantías. Al usarlo, aceptas que recopilamos el mínimo de datos necesario para funcionar correctamente.</p>
    '''

@app.route('/privacy')
def privacy():
    return '''
    <h1>Política de Privacidad</h1>
    <p>No recopilamos ni almacenamos datos personales de los usuarios. Solo se usan los mensajes necesarios para responder a comandos del bot.</p>
    '''

def keep_alive():
    from threading import Thread
    def run():
        app.run(host='0.0.0.0', port=3000)
    t = Thread(target=run)
    t.start()
