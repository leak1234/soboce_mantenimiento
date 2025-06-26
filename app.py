from flask import Flask
from auth import auth_bp
from routes.inicio import inicio_bp
from routes.mantenimientos import mantenimientos_bp
from routes.equipos import equipos_bp
from routes.inventario import inventario_bp
from routes.reportes import reportes_bp
from routes.usuarios import usuarios_bp
from routes.configuracion import configuracion_bp
from routes.horometro import horometro_bp  
from routes.frecuencias import frecuencias_bp


app = Flask(__name__)
app.secret_key = 'clave_de_prueba_123'

# Registrar todos los blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(inicio_bp)
app.register_blueprint(mantenimientos_bp)
app.register_blueprint(equipos_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(configuracion_bp)
app.register_blueprint(horometro_bp) 
app.register_blueprint(frecuencias_bp) 

if __name__ == '__main__':
    app.run(debug=True)
