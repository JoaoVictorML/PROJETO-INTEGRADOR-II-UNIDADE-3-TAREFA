from models.Geral import Base, engine
from repositories.admin_repository import AdminRepository

# Cria as tabelas (se ainda não existirem)
Base.metadata.create_all(engine)

# Dados do primeiro administrador
dados_admin = {
    "name": "Administrador",
    "email": "administrator@gmail.com",
    "password": "admi123",
    "position": "Administrador",
    "salario": "0",          # agora usa "salario" (não mais "wage")
    "phone": "",
    "active": True,
}

ok, result = AdminRepository.create(dados_admin)

if ok:
    print("✅ Administrador criado com sucesso!")
    print(f"   ID: {result['id']}")
    print(f"   Nome: {result['name']}")
    print(f"   E-mail: {result['email']}")
else:
    print(f"❌ Erro ao criar administrador: {result}")