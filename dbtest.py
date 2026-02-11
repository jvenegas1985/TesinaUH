import mysql.connector
from mysql.connector import Error

try:
    # Establecer la conexión con la base de datos
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Usuario1',
        database='proyecto'
    )

    if connection.is_connected():
        print("✅ Conexión exitosa a la base de datos MySQL")

        # Crear un cursor para ejecutar las consultas
        cursor = connection.cursor()

        # Realizar una consulta SQL para obtener los datos
        cursor.execute("SELECT id, cedula, nombre, apellido1, genero, telefono_contacto FROM residentes")

        # Obtener todos los resultados de la consulta
        residentes = cursor.fetchall()

        # Mostrar los datos
        print("📋 Datos de los residentes:")
        for residente in residentes:
            print(f"ID: {residente[0]}, Cedula: {residente[1]}, Nombre: {residente[2]}, Apellido: {residente[3]}, Género: {residente[4]}, Teléfono: {residente[5]}")

        # Cerrar el cursor
        cursor.close()

except Error as e:
    print(f"❌ Error al conectar a MySQL: {e}")

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("🔌 Conexión cerrada")
