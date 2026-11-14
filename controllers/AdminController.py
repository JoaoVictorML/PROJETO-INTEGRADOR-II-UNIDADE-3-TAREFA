from models.Geral import Session
from models.Admin import Admin

def cadastrar_usuario(fullname, email, cpf_input, password, confirm_password):
    session = Session()
    try:
        usuario_existente = session.query(Admin).filter(Admin.login == email).first()
        if usuario_existente:
            return False, "Este e-mail já está cadastrado!"

        admin = Admin()
        admin.name = fullname      
        admin.login = email        
        admin.cpf = cpf_input 
        admin.password = password
        admin.cpassword = confirm_password 

        if admin.password != admin.cpassword:
            return False, "A senha e a confirmação de senha devem ser iguais."
        
        session.add(admin)
        session.commit()
        return True, "Usuário cadastrado com sucesso!"
        
    except Exception as e:
        session.rollback()
        print("❌ ERRO REAL DO MYSQL:", str(e))
        return False, "Erro ao cadastrar usuário no banco de dados."
    finally:
        session.close()