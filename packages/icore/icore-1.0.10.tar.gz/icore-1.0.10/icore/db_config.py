import sqlite3

# Criar tabela de configuração


def create_table():
    connection = sqlite3.connect("idash.db")
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS configuracao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campo TEXT NOT NULL UNIQUE,
                    valor TEXT NOT NULL,
                    tipo TEXT NOT NULL
                    )"""
    )

    connection.commit()
    connection.close()


def set(campo, valor, tipo):
    connection = sqlite3.connect("idash.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO configuracao (campo, valor,tipo) VALUES (?, ?, ? )",
        (campo, valor, tipo),
    )
    connection.commit()
    connection.close()


def get(campo):
    connection = sqlite3.connect("idash.db")
    cursor = connection.cursor()

    cursor.execute("SELECT valor FROM configuracao where campo = '" + campo + "'")
    items = cursor.fetchall()
    connection.close()

    if items:
        return items[0][0]
    else:
        return False


def get_tipo(tipo):
    connection = sqlite3.connect("idash.db")
    cursor = connection.cursor()

    cursor.execute("SELECT campo,valor FROM configuracao where tipo = '" + tipo + "'")
    resultados = {}
    if cursor.rowcount == 0:
        print("Nenhum resultado encontrado para o tipo:", tipo)
        return False
    else:
        for linha in cursor.fetchall():
            resultados[linha[0]] = linha[1]
        connection.close()

    return resultados


def lista_configuracao():
    connection = sqlite3.connect("idash.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM configuracao")
    items = cursor.fetchall()

    connection.close()
    return items


# create_table()
# set("illi_banco_url", "127.0.0.2")
# set("illi_banco_usuario", "root")
# set("illi_banco_senha", "a7v400mx")
# set("url_base_fotos", "https://www.illi.com.br/fotos/")

# print(get("illi_banco_url"))
