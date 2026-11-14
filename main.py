from flask import Flask
# 1. Importar Base e engine PRIMEIRO
from models.Geral import Base, engine

# 2. Importar TODOS os modelos ANTES de criar as tabelas
from models.User import User
from models.Admin import Admin
from models.Product import Product
from models.Employee import Employee

# 3. Registrar as rotas
from routes.views import views_bp
from routes.api import api_bp
from routes.admin import admin_bp
from routes.employee import employee_bp
from routes.user import user_bp
from routes.product import product_bp

# 4. Criar as tabelas NO BANCO
Base.metadata.create_all(engine)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_ifce'

# 5. Registrar Blueprints
app.register_blueprint(views_bp)
app.register_blueprint(api_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(user_bp)
app.register_blueprint(product_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)