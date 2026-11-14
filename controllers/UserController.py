from sqlalchemy import func
from models.Geral import Session
from models.User import User


def cadastrar_usuario(nome, email, password):
    session = Session()
    try:
        nome = (nome or "").strip()
        email = (email or "").strip().lower()
        password = (password or "").strip()

        if not nome or not email or not password:
            return False, "Preencha nome, e-mail e senha."

        usuario_existente = session.query(User).filter(func.lower(User.login) == email).first()
        if usuario_existente:
            return False, "Este e-mail já está cadastrado!"

        user = User()
        user.nome = nome
        user.login = email
        user.cpf = ""
        user.password = password

        session.add(user)
        session.commit()
        session.refresh(user)
        return True, user.to_dict()

    except Exception as e:
        session.rollback()
        print("❌ ERRO REAL DO MYSQL:", str(e))
        return False, "Erro ao cadastrar usuário no banco de dados."
    finally:
        session.close()