

def insert_user(db_conn, usr):
    cursor = db_conn.cursor()

    query = "INSERT INTO usuarios (usr_id,username, password) VALUES (%s,%s, %s)"
    cursor.execute(query, usr)
    db_conn.commit()


def query_users(db_conn):
    cur = db_conn.cursor()

    # Obtiene todos los datos de tabla
    query = "SELECT * FROM usuarios"
    cur.execute(query)

    usuarios = [
        dict(id=row[0], user=row[1], password=row[2])
        for row in cur.fetchall()
    ]
    if usuarios is not None:
        return usuarios
    else:
        return None


'''
def query_data(conn, username, password):
    cur = conn.cursor()

    # Obtiene usario por la opcion recibida (nombre)
    query = "SELECT * FROM usuarios WHERE username = %s;"
    print(query)
    cur.execute(query, username)

    username = [
        dict(id=row[0], usrname=row[1], pwd=row[2])
        for row in cur.fetchall()
    ]

    print(username)

    if username is not None:
        return True
    else:
        return False
'''


def update_usr(conn, usr):
    # Modifica nuevo usuario
    query = ''' UPDATE usuarios SET username = %s, password = %s WHERE usr_id=%s '''
    cur = conn.cursor()
    cur.execute(query, usr)
    conn.commit()


def delete_user(conn, id_borrar):
    # Elimina usuario con id recibido por parametro
    query = " DELETE FROM usuarios WHERE usr_id = %s;"
    cur = conn.cursor()
    cur.execute(query, (id_borrar,))
    conn.commit()
