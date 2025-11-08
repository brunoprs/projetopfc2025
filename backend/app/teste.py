from app import create_app, db
from sqlalchemy import text  # ✅ Import obrigatório

app = create_app()

try:
    with app.app_context():
        # ✅ Usa text() corretamente
        db.session.execute(text("SELECT 1"))
    print("✅ Conexão com o banco de dados via Flask bem-sucedida!")
except Exception as e:
    print("❌ Erro ao conectar via Flask:", e)
