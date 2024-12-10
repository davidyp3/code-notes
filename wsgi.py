from app import app, init_db

# Inicializa o banco de dados
init_db()

if __name__ == "__main__":
    app.run()
