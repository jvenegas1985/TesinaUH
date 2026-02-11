import mysql.connector
from faker import Faker
import random

# Configura Faker y conexión
fake = Faker('es_ES')

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Usuario1",
    database="proyecto"
)

cursor = db.cursor()

# Opciones para ENUMs
generos = ['Masculino', 'Femenino', 'Otro']
estado_civil = ['Soltero', 'Casado', 'Viudo', 'Divorciado']
movilidad = ['Independiente', 'Con ayuda', 'Dependiente']
estado_mental = ['Lúcido', 'Desorientado', 'Demencia', 'Otro']

# Insertar residentes
for _ in range(5):
    nombre = fake.first_name()
    apellido1 = fake.last_name()
    apellido2 = fake.last_name()
    cedula = fake.unique.random_number(digits=9)
    fecha_nacimiento = fake.date_of_birth(minimum_age=65, maximum_age=90)
    genero = random.choice(generos)
    civil = random.choice(estado_civil)
    nacionalidad = fake.country()
    direccion = fake.address()
    telefono = fake.phone_number()
    emergencia_nombre = fake.name()
    emergencia_parentesco = random.choice(['Hijo', 'Nieto', 'Hermano', 'Amigo'])
    emergencia_telefono = fake.phone_number()
    condiciones = fake.sentence()
    medicamentos = fake.words(nb=3, unique=True)
    movilidad_val = random.choice(movilidad)
    estado_mental_val = random.choice(estado_mental)

    cursor.execute("""
        INSERT INTO residentes (
            nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil, nacionalidad,
            direccion, telefono_contacto, contacto_emergencia_nombre, contacto_emergencia_parentesco,
            contacto_emergencia_telefono, condiciones_medicas, medicamentos_actuales, movilidad,
            estado_mental, activo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
    """, (
        nombre, apellido1, apellido2, str(cedula), fecha_nacimiento, genero, civil, nacionalidad,
        direccion, telefono, emergencia_nombre, emergencia_parentesco, emergencia_telefono,
        condiciones, ', '.join(medicamentos), movilidad_val, estado_mental_val
    ))

    residente_id = cursor.lastrowid

    # Insertar historial médico
    for _ in range(random.randint(2, 3)):
        cursor.execute("""
            INSERT INTO historial_medico (residente_id, fecha, diagnostico, observaciones)
            VALUES (%s, %s, %s, %s)
        """, (
            residente_id,
            fake.date_between(start_date='-2y', end_date='today'),
            fake.sentence(nb_words=6),
            fake.paragraph()
        ))

    # Insertar medicación
    for _ in range(random.randint(2, 3)):
        fecha_ini = fake.date_between(start_date='-1y', end_date='-1m')
        fecha_fin = fake.date_between(start_date=fecha_ini, end_date='today')
        cursor.execute("""
            INSERT INTO medicacion (residente_id, medicamento, dosis, frecuencia, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            residente_id,
            fake.word().capitalize(),
            f"{random.randint(1, 2)} cápsulas",
            random.choice(['1 vez al día', '2 veces al día', 'Cada 8 horas']),
            fecha_ini,
            fecha_fin
        ))

db.commit()
cursor.close()
db.close()

print("Datos generados exitosamente.")
