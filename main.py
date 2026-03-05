import mysql.connector
from flask import  jsonify, make_response, Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import database as db
from datetime import datetime, time
from werkzeug.security import check_password_hash,generate_password_hash
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address








def role_required(*roles_permitidos):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                flash("Debes iniciar sesión.", "warning")
                return redirect("/login")

            if current_user.rol not in roles_permitidos:
                flash("No tienes permisos para realizar esta acción.", "danger")
                return redirect(request.referrer or "/")

            return func(*args, **kwargs)
        return wrapper
    return decorator





app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://" 
)








login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # página a redirigir si no está autenticado

class User(UserMixin):
    def __init__(self, id, username, rol, nombre):
        self.id = id
        self.username = username
        self.rol = rol
        self.nombre = nombre

    def get_id(self):
        return f"user_{self.id}"
    
class Familiar(UserMixin):
    def __init__(self, id, username, password, nombre, cedula, email, activo=True):
        self.id = id
        self.username = username
        self.password = password
        self.nombre = nombre
        self.cedula = cedula
        self.email = email
        self.activo = activo
        self.rol = 'familiar'  # Rol fijo para identificar
    
    def get_id(self):
        return f"familiar_{self.id}"


@login_manager.user_loader
def load_user(user_id):
    try:
        from database import database
        cursor = database.cursor(dictionary=True)

        if user_id.startswith('familiar_'):
            familiar_id = user_id.replace('familiar_', '')

            cursor.execute("""
                SELECT id, username, nombre, cedula, email, activo
                FROM familiares 
                WHERE id = %s AND activo = TRUE
            """, (familiar_id,))

            familiar = cursor.fetchone()
            cursor.close()

            if familiar:
                return Familiar(
                    id=familiar['id'],
                    username=familiar['username'],
                    password=None,
                    nombre=familiar['nombre'],
                    cedula=familiar['cedula'],
                    email=familiar['email'],
                    activo=familiar['activo']
                )
            return None

        elif user_id.startswith('user_'):
            user_id_clean = user_id.replace('user_', '')

            cursor.execute("""
                SELECT id, username, rol, nombre, activo
                FROM usuarios 
                WHERE id = %s AND activo = 1
            """, (user_id_clean,))

            user = cursor.fetchone()
            cursor.close()

            if user:
                return User(
                    id=user['id'],
                    username=user['username'],
                    rol=user['rol'],
                    nombre=user['nombre']
                )
            return None

        return None

    except Exception as e:
        print(f"⚠️ Error en load_user: {e}")
        return None

@app.context_processor
def inject_user():
    return dict(current_user=current_user)  # usar current_user de flask_login

@app.route('/', methods=['GET'])
def index_publico():
    return render_template('login.html')

from flask import session

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('usuario')
        password = request.form.get('contraseña')

        cursor = db.database.cursor(dictionary=True)

        # 1️⃣ Buscar en usuarios internos
        cursor.execute("""
            SELECT id, username, password, rol, nombre, activo
            FROM usuarios
            WHERE username = %s
        """, (username,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            if user['activo'] == 0:
                flash("Tu cuenta está inactiva. Contacta al administrador.", "warning")
                return render_template('login.html')

            if not check_password_hash(user['password'], password):
                flash("Contraseña incorrecta.", "danger")
                return render_template('login.html')

            user_obj = User(
                id=user['id'],
                username=user['username'],
                rol=user['rol'],
                nombre=user['nombre']
            )

            login_user(user_obj)
            session['rol'] = user_obj.rol
            session['nombre'] = user_obj.nombre
            session['tipo_usuario'] = 'interno'
            session['mostrar_modal'] = True

            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for('index_admin'))

        # 2️⃣ Buscar en familiares - VERSIÓN CORREGIDA
        cursor.execute("""
            SELECT id, username, password, nombre, cedula, email, activo
            FROM familiares
            WHERE username = %s
        """, (username,))
        familiar = cursor.fetchone()
        cursor.close()

        if familiar:
            if familiar['activo'] == 0:
                flash("Tu cuenta está inactiva. Contacta al administrador.", "warning")
                return render_template('login.html')

            if not check_password_hash(familiar['password'], password):
                flash("Contraseña incorrecta.", "danger")
                return render_template('login.html')

            # 🔴 CORREGIDO: Agregar password como parámetro
            familiar_obj = Familiar(
                id=familiar['id'],
                username=familiar['username'],
                password=familiar['password'],  # ← ESTE FALTABA
                nombre=familiar['nombre'],
                cedula=familiar['cedula'],
                email=familiar['email'],
                activo=familiar['activo']
            )

            login_user(familiar_obj)
            session['rol'] = 'familiar'
            session['nombre'] = familiar_obj.nombre
            session['tipo_usuario'] = 'familiar'

            # Actualizar último acceso
            cursor_up = db.database.cursor()
            cursor_up.execute(
                "UPDATE familiares SET ultimo_acceso = NOW() WHERE id = %s",
                (familiar['id'],)
            )
            db.database.commit()
            cursor_up.close()

            flash(f"Bienvenido {familiar_obj.nombre}", "success")
            return redirect(url_for('familiar_dashboard'))

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template('login.html')

@app.errorhandler(429)
def ratelimit_error(e):
    flash("Demasiados intentos. Espera un momento e intenta de nuevo.", "danger")
    return render_template('login.html'), 429




@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "success")
    return redirect(url_for('login'))

@app.route('/limpiar_modal', methods=['POST'])
@login_required
def limpiar_modal():
    session.pop('mostrar_modal', None)
    return '', 204


@app.route('/familiar/dashboard')
@login_required
def familiar_dashboard():
    """Dashboard para familiares - muestra solo los residentes asignados"""
    
    # Verificar que sea familiar
    if session.get('tipo_usuario') != 'familiar':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))
    
    # Obtener el ID real del familiar
    familiar_id = current_user.real_id if hasattr(current_user, 'real_id') else str(current_user.id).replace('familiar_', '')
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener residentes asignados al familiar
        cursor.execute("""
            SELECT 
                r.id,
                r.cedula,
                r.nombre,
                r.apellido1,
                r.apellido2,
                r.fecha_nacimiento,
                fr.parentesco,
                fr.es_contacto_principal,
                TIMESTAMPDIFF(YEAR, r.fecha_nacimiento, CURDATE()) as edad,
                CONCAT(r.nombre, ' ', r.apellido1, ' ', COALESCE(r.apellido2, '')) as nombre_completo,
                c.numero as cama_actual
            FROM residentes r
            INNER JOIN familiar_residente fr ON r.id = fr.residente_id
            LEFT JOIN asignacion_camas ac ON r.id = ac.residente_id AND ac.estado = 'Activa'
            LEFT JOIN camas c ON ac.cama_id = c.id
            WHERE fr.familiar_id = %s AND fr.activo = 1 AND r.activo = 1
            ORDER BY r.nombre, r.apellido1
        """, (familiar_id,))
        
        residentes = cursor.fetchall()
        
        # Para cada residente, obtener las últimas 3 actividades
        for residente in residentes:
            cursor.execute("""
                SELECT 
                    b.tipo,
                    b.descripcion,
                    DATE_FORMAT(b.fecha_hora, '%d/%m/%Y %H:%i') as fecha,
                    u.nombre as personal_nombre
                FROM bitacora_pacientes b
                LEFT JOIN usuarios u ON b.personal_id = u.id
                WHERE b.residente_id = %s AND b.estado = 'activo'
                ORDER BY b.fecha_hora DESC
                LIMIT 3
            """, (residente['id'],))
            
            residente['ultimas_actividades'] = cursor.fetchall()
            
            # Contar actividades de hoy
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM bitacora_pacientes
                WHERE residente_id = %s 
                  AND DATE(fecha_hora) = CURDATE()
                  AND estado = 'activo'
            """, (residente['id'],))
            
            residente['actividades_hoy'] = cursor.fetchone()['total']
        
    except Exception as e:
        print(f"Error en familiar_dashboard: {e}")
        residentes = []
        flash(f"Error al cargar datos: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return render_template('modulos/familiares/dashboard.html',
                         residentes=residentes,
                         hoy=datetime.now().strftime('%d/%m/%Y'))




@app.route('/admin/familiares')
@login_required
@role_required('administrador', 'asistente_administrativo')
def listar_familiares():
    """Lista todos los familiares registrados"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT f.*, 
                   COUNT(fr.residente_id) as total_residentes,
                   GROUP_CONCAT(CONCAT(r.nombre, ' ', r.apellido1) SEPARATOR ', ') as residentes_asignados
            FROM familiares f
            LEFT JOIN familiar_residente fr ON f.id = fr.familiar_id AND fr.activo = 1
            LEFT JOIN residentes r ON fr.residente_id = r.id
            GROUP BY f.id
            ORDER BY f.nombre, f.apellido1
        """)
        familiares = cursor.fetchall()
        
    except Exception as e:
        print(f"Error listando familiares: {e}")
        familiares = []
        flash(f"Error al cargar familiares: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return render_template('modulos/usuarios/familiares.html', familiares=familiares)




@app.route('/admin/familiares/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def nuevo_familiar():
    """Crea un nuevo familiar"""
    cursor = db.database.cursor(dictionary=True)
    
    if request.method == 'POST':
        cedula = request.form.get('cedula', '').strip()
        nombre = request.form.get('nombre', '').strip().upper()
        apellido1 = request.form.get('apellido1', '').strip().upper()
        apellido2 = request.form.get('apellido2', '').strip().upper()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Obtener residentes seleccionados
        residentes_asignados = request.form.getlist('residentes[]')
        
        print(f"🔍 DEBUG - Residentes seleccionados: {residentes_asignados}")
        
        # Validaciones
        if not all([cedula, nombre, apellido1, username, password]):
            flash("Cédula, nombre, apellido, usuario y contraseña son obligatorios", "danger")
            return redirect(url_for('nuevo_familiar'))
        
        try:
            # Verificar cédula única
            cursor.execute("SELECT id FROM familiares WHERE cedula = %s", (cedula,))
            if cursor.fetchone():
                flash(f"Ya existe un familiar con cédula {cedula}", "danger")
                return redirect(url_for('nuevo_familiar'))
            
            # Verificar username único
            cursor.execute("SELECT id FROM familiares WHERE username = %s", (username,))
            if cursor.fetchone():
                flash(f"El username {username} ya está en uso", "danger")
                return redirect(url_for('nuevo_familiar'))
            
            # Verificar email único (si se proporcionó)
            if email:
                cursor.execute("SELECT id FROM familiares WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash(f"El email {email} ya está registrado", "danger")
                    return redirect(url_for('nuevo_familiar'))
            
            # Hash de contraseña
            password_hash = generate_password_hash(password)
            
            # Insertar familiar
            cursor.execute("""
                INSERT INTO familiares 
                (cedula, nombre, apellido1, apellido2, telefono, email, username, password, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (cedula, nombre, apellido1, apellido2, telefono, email, username, password_hash, current_user.id))
            
            familiar_id = cursor.lastrowid
            print(f"✅ Familiar creado con ID: {familiar_id}")
            
            # Asignar residentes - PARTE CORREGIDA
            if residentes_asignados and len(residentes_asignados) > 0:
                asignaciones_exitosas = 0
                for residente_id in residentes_asignados:
                    try:
                        # Obtener parentesco específico para este residente
                        parentesco = request.form.get(f'parentesco_{residente_id}', 'OTRO')
                        es_principal = 1 if request.form.get(f'principal_{residente_id}') == 'on' else 0
                        
                        print(f"   Asignando residente {residente_id}: parentesco={parentesco}, principal={es_principal}")
                        
                        # Insertar en familiar_residente
                        cursor.execute("""
                            INSERT INTO familiar_residente 
                            (familiar_id, residente_id, parentesco, es_contacto_principal, 
                             puede_ver_historial, puede_ver_medicacion, activo)
                            VALUES (%s, %s, %s, %s, 1, 1, 1)
                        """, (familiar_id, residente_id, parentesco, es_principal))
                        
                        asignaciones_exitosas += 1
                        
                    except Exception as e:
                        print(f"❌ Error asignando residente {residente_id}: {str(e)}")
                        continue
                
                print(f"✅ {asignaciones_exitosas} residentes asignados correctamente")
            else:
                print("ℹ️ No se seleccionaron residentes")
            
            db.database.commit()
            flash(f"Familiar {nombre} {apellido1} creado exitosamente con {len(residentes_asignados)} residente(s)", "success")
            return redirect(url_for('listar_familiares'))
            
        except Exception as e:
            db.database.rollback()
            print(f"❌ Error al crear familiar: {str(e)}")
            flash(f"Error al crear familiar: {str(e)}", "danger")
            import traceback
            traceback.print_exc()
    
    # GET: cargar residentes disponibles
    cursor.execute("""
        SELECT id, cedula, nombre, apellido1, apellido2 
        FROM residentes 
        WHERE activo = 1 
        ORDER BY nombre, apellido1
    """)
    residentes = cursor.fetchall()
    cursor.close()
    
    return render_template('modulos/usuarios/nuevo_familiar.html', residentes=residentes)



@app.route('/admin/familiares/<int:familiar_id>/residentes')
@login_required
@role_required('administrador', 'asistente_administrativo')
def get_familiar_residentes(familiar_id):
    """API para obtener los residentes asignados a un familiar"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Verificar que el familiar existe
        cursor.execute("SELECT id, nombre, apellido1 FROM familiares WHERE id = %s", (familiar_id,))
        familiar = cursor.fetchone()
        
        if not familiar:
            return jsonify({'error': 'Familiar no encontrado'}), 404
        
        # Obtener residentes asignados ACTIVOS
        cursor.execute("""
            SELECT 
                r.id,
                r.cedula,
                r.nombre,
                r.apellido1,
                r.apellido2,
                fr.parentesco,
                fr.es_contacto_principal
            FROM familiar_residente fr
            INNER JOIN residentes r ON fr.residente_id = r.id
            WHERE fr.familiar_id = %s AND fr.activo = 1 AND r.activo = 1
            ORDER BY r.nombre, r.apellido1
        """, (familiar_id,))
        
        residentes = cursor.fetchall()
        
        print(f"Residentes encontrados para familiar {familiar_id}: {len(residentes)}")  # DEBUG
        
        return jsonify({
            'success': True,
            'familiar': {
                'id': familiar['id'],
                'nombre': f"{familiar['nombre']} {familiar['apellido1']}"
            },
            'residentes': residentes,
            'total': len(residentes)
        })
        
    except Exception as e:
        print(f"Error en get_familiar_residentes: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()



@app.route('/admin/familiares/<int:familiar_id>/residentes-disponibles')
@login_required
@role_required('administrador', 'asistente_administrativo')
def get_residentes_disponibles(familiar_id):
    """API para obtener todos los residentes y marcar los asignados"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener todos los residentes activos
        cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2
            FROM residentes 
            WHERE activo = 1 
            ORDER BY nombre, apellido1
        """)
        todos_residentes = cursor.fetchall()
        
        # Obtener asignaciones actuales del familiar
        cursor.execute("""
            SELECT residente_id, parentesco, es_contacto_principal
            FROM familiar_residente
            WHERE familiar_id = %s AND activo = 1
        """, (familiar_id,))
        
        asignaciones = cursor.fetchall()
        asignados_dict = {a['residente_id']: a for a in asignaciones}
        
        # Combinar datos
        residentes = []
        for r in todos_residentes:
            residentes.append({
                'id': r['id'],
                'cedula': r['cedula'],
                'nombre': r['nombre'],
                'apellido1': r['apellido1'],
                'apellido2': r['apellido2'],
                'asignado': r['id'] in asignados_dict,
                'parentesco': asignados_dict.get(r['id'], {}).get('parentesco', 'OTRO'),
                'principal': asignados_dict.get(r['id'], {}).get('es_contacto_principal', False)
            })
        
        return jsonify({'residentes': residentes})
        
    except Exception as e:
        print(f"Error en get_residentes_disponibles: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()


@app.route('/admin/familiares/<int:familiar_id>/datos')
@login_required
@role_required('administrador', 'asistente_administrativo')
def get_familiar_datos(familiar_id):
    """API para obtener datos de un familiar"""
    cursor = db.database.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2, 
                   fecha_nacimiento, genero, telefono, email, direccion, 
                   username, activo
            FROM familiares 
            WHERE id = %s
        """, (familiar_id,))
        
        familiar = cursor.fetchone()
        
        if not familiar:
            return jsonify({'error': 'Familiar no encontrado'}), 404
        
        # Formatear fecha
        if familiar.get('fecha_nacimiento'):
            if hasattr(familiar['fecha_nacimiento'], 'strftime'):
                familiar['fecha_nacimiento'] = familiar['fecha_nacimiento'].strftime('%Y-%m-%d')
        
        return jsonify(familiar)
        
    except Exception as e:
        print(f"Error en get_familiar_datos: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()



@app.route('/admin/familiares/<int:familiar_id>/editar', methods=['POST'])
@login_required
@role_required('administrador')
def editar_familiar(familiar_id):
    """Actualiza datos de un familiar"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Verificar que el familiar existe
        cursor.execute("SELECT id FROM familiares WHERE id = %s", (familiar_id,))
        if not cursor.fetchone():
            flash("Familiar no encontrado", "danger")
            return redirect(url_for('listar_familiares'))
        
        # Obtener datos del formulario
        cedula = request.form.get('cedula', '').strip()
        nombre = request.form.get('nombre', '').strip().upper()
        apellido1 = request.form.get('apellido1', '').strip().upper()
        apellido2 = request.form.get('apellido2', '').strip().upper()
        fecha_nacimiento = request.form.get('fecha_nacimiento') or None
        genero = request.form.get('genero', '').strip()  # ← ESTE ES EL CAMPO PROBLEMÁTICO
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip().upper()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        activo = 1 if request.form.get('activo') else 0
        
        # 🔴 VALIDACIÓN IMPORTANTE: El género debe ser uno de los valores permitidos
        valores_validos_genero = ['Masculino', 'Femenino', 'Otro', '']
        if genero and genero not in valores_validos_genero:
            genero = ''  # Si no es válido, lo dejamos vacío
            print(f"Género inválido recibido: {genero}")
        
        # Validaciones básicas
        if not all([cedula, nombre, apellido1, username]):
            flash("Cédula, nombre, apellido y usuario son obligatorios", "danger")
            return redirect(url_for('listar_familiares'))
        
        # Verificar cédula única (excluyendo este registro)
        cursor.execute("SELECT id FROM familiares WHERE cedula = %s AND id != %s", (cedula, familiar_id))
        if cursor.fetchone():
            flash(f"Ya existe otro familiar con cédula {cedula}", "danger")
            return redirect(url_for('listar_familiares'))
        
        # Verificar username único
        cursor.execute("SELECT id FROM familiares WHERE username = %s AND id != %s", (username, familiar_id))
        if cursor.fetchone():
            flash(f"El nombre de usuario {username} ya está en uso", "danger")
            return redirect(url_for('listar_familiares'))
        
        # Verificar email único (si se proporcionó)
        if email:
            cursor.execute("SELECT id FROM familiares WHERE email = %s AND id != %s", (email, familiar_id))
            if cursor.fetchone():
                flash(f"El email {email} ya está registrado", "danger")
                return redirect(url_for('listar_familiares'))
        
        # 🔴 CORRECCIÓN: Manejar el género NULL si está vacío
        if genero == '':
            genero = None
        
        # Actualizar familiar
        if password and len(password) >= 6:
            password_hash = generate_password_hash(password)
            cursor.execute("""
                UPDATE familiares SET
                    cedula = %s,
                    nombre = %s,
                    apellido1 = %s,
                    apellido2 = %s,
                    fecha_nacimiento = %s,
                    genero = %s,
                    telefono = %s,
                    email = %s,
                    direccion = %s,
                    username = %s,
                    password = %s,
                    activo = %s
                WHERE id = %s
            """, (cedula, nombre, apellido1, apellido2, fecha_nacimiento, 
                  genero, telefono, email, direccion, username, password_hash, activo, familiar_id))
        else:
            cursor.execute("""
                UPDATE familiares SET
                    cedula = %s,
                    nombre = %s,
                    apellido1 = %s,
                    apellido2 = %s,
                    fecha_nacimiento = %s,
                    genero = %s,
                    telefono = %s,
                    email = %s,
                    direccion = %s,
                    username = %s,
                    activo = %s
                WHERE id = %s
            """, (cedula, nombre, apellido1, apellido2, fecha_nacimiento, 
                  genero, telefono, email, direccion, username, activo, familiar_id))
        
        # Actualizar asignaciones de residentes
        # Primero, desactivar todas las asignaciones actuales
        cursor.execute("UPDATE familiar_residente SET activo = 0 WHERE familiar_id = %s", (familiar_id,))
        
        # Obtener residentes seleccionados
        residentes_asignados = request.form.getlist('residentes[]')
        
        if residentes_asignados:
            for residente_id in residentes_asignados:
                parentesco = request.form.get(f'parentesco_{residente_id}', 'OTRO')
                es_principal = 1 if request.form.get(f'principal_{residente_id}') == 'on' else 0
                
                # Verificar si ya existía una asignación
                cursor.execute("""
                    SELECT id FROM familiar_residente 
                    WHERE familiar_id = %s AND residente_id = %s
                """, (familiar_id, residente_id))
                
                existente = cursor.fetchone()
                
                if existente:
                    # Actualizar existente
                    cursor.execute("""
                        UPDATE familiar_residente SET
                            parentesco = %s,
                            es_contacto_principal = %s,
                            activo = 1
                        WHERE id = %s
                    """, (parentesco, es_principal, existente['id']))
                else:
                    # Insertar nueva
                    cursor.execute("""
                        INSERT INTO familiar_residente 
                        (familiar_id, residente_id, parentesco, es_contacto_principal, activo)
                        VALUES (%s, %s, %s, %s, 1)
                    """, (familiar_id, residente_id, parentesco, es_principal))
        
        db.database.commit()
        flash("Familiar actualizado correctamente", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        print(f"Error en editar_familiar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
    
    return redirect(url_for('listar_familiares'))


@app.route('/familiar/bitacora/<int:residente_id>')
@login_required
def familiar_ver_bitacora(residente_id):
    """Familiar ve la bitácora completa de un residente (solo consulta)"""
    
    # Verificar que sea familiar
    if session.get('tipo_usuario') != 'familiar':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))
    
    familiar_id = current_user.real_id if hasattr(current_user, 'real_id') else str(current_user.id).replace('familiar_', '')
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Verificar que el familiar tenga acceso a este residente
        cursor.execute("""
            SELECT fr.*, r.nombre, r.apellido1, r.apellido2
            FROM familiar_residente fr
            JOIN residentes r ON fr.residente_id = r.id
            WHERE fr.familiar_id = %s 
              AND fr.residente_id = %s 
              AND fr.activo = 1
        """, (familiar_id, residente_id))
        
        relacion = cursor.fetchone()
        
        if not relacion:
            flash("No tienes acceso a este residente", "danger")
            return redirect(url_for('familiar_dashboard'))
        
        # Obtener información del residente
        cursor.execute("""
            SELECT 
                r.*,
                TIMESTAMPDIFF(YEAR, r.fecha_nacimiento, CURDATE()) as edad,
                CONCAT(r.nombre, ' ', r.apellido1, ' ', COALESCE(r.apellido2, '')) as nombre_completo
            FROM residentes r
            WHERE r.id = %s
        """, (residente_id,))
        
        residente = cursor.fetchone()
        
        # Obtener bitácora completa (últimos 50 registros)
        cursor.execute("""
            SELECT 
                b.*,
                u.nombre as personal_nombre,
                DATE_FORMAT(b.fecha_hora, '%d/%m/%Y %H:%i') as fecha_formateada,
                DATE_FORMAT(b.fecha_hora, '%H:%i') as hora
            FROM bitacora_pacientes b
            LEFT JOIN usuarios u ON b.personal_id = u.id
            WHERE b.residente_id = %s AND b.estado = 'activo'
            ORDER BY b.fecha_hora DESC
            LIMIT 50
        """, (residente_id,))
        
        registros = cursor.fetchall()
        
        # Estadísticas por tipo
        cursor.execute("""
            SELECT 
                tipo,
                COUNT(*) as cantidad
            FROM bitacora_pacientes
            WHERE residente_id = %s AND estado = 'activo'
            GROUP BY tipo
            ORDER BY cantidad DESC
        """, (residente_id,))
        
        stats_por_tipo = cursor.fetchall()
        
    except Exception as e:
        print(f"Error en familiar_ver_bitacora: {e}")
        flash(f"Error al cargar bitácora: {str(e)}", "danger")
        return redirect(url_for('familiar_dashboard'))
    finally:
        cursor.close()
    
    return render_template('modulos/familiares/ver_bitacora.html',
                         residente=residente,
                         relacion=relacion,
                         registros=registros,
                         stats_por_tipo=stats_por_tipo)





@app.route('/residentes',methods=['GET'])
@login_required
@role_required('administrador','medico', 'asistente_administrativo')
def index_residentes():
    try:
        cursor = db.database.cursor()
        cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion, activo 
            FROM residentes 
            ORDER BY id DESC LIMIT 20 OFFSET 0
        """)
        datos = cursor.fetchall()
        columnames = [col[0] for col in cursor.description]
        arreglo = [dict(zip(columnames, record)) for record in datos]
    except Exception as e:
        print("ERROR EN RESIDENTES:", e)
        arreglo = []
    finally:
        cursor.close()

    response = make_response(render_template('modulos/clientes/residentes.html', residentes=arreglo))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Ruta para crear un nuevo cliente
@app.route('/create')
@login_required
@role_required('administrador', 'asistente_administrativo')
def index_create():
    return render_template('modulos/clientes/create.html')




@app.route('/edit/<string:id>', methods=['GET'])
@login_required
@role_required('administrador','medico', 'asistente_administrativo')
def index_editar(id):  # Asegúrate de que se reciba `id`
    cursor = db.database.cursor()  # Establecer conexión
    cursor.execute("SELECT * FROM residentes WHERE id = %s", (id,))
    datos = cursor.fetchall() 
    arreglo = []
    columnames = [col[0] for col in cursor.description]
    for record in datos:
         arreglo.append(dict(zip(columnames, record)))
    
    cursor.close()  # Cerrar el cursor
    return render_template('modulos/clientes/edit.html', arreglo=arreglo)


@app.route('/eliminar/<string:id>',methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def eliminar_residente(id):
    cursor = db.database.cursor() # Establecer conexión
    cursor.execute("DELETE from RESIDENTES where id= %s", (id,))
    db.database.commit()   
    cursor.close()  # Cerrar el cursor  
    
  
    return redirect(url_for('index_residentes'))




# Ruta para guardar un nuevo residente
@app.route('/modulos/clientes/create/guardar', methods=['POST'])
@login_required
@role_required('administrador', 'asistente_administrativo') 
def btn_cliente_guardar():
    # ———————— Datos obligatorios del formulario ————————
    nombre = request.form.get('nombre', '').strip().upper()
    apellido1 = request.form.get('apellido1', '').strip().upper()
    apellido2 = request.form.get('apellido2', '').strip().upper()
    cedula = request.form.get('cedula', '').strip()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()

    # Estos cuatro campos son ENUM en la BD
    genero = request.form.get('genero', '').strip()
    estado_civil = request.form.get('estado_civil', '').strip()
    movilidad = request.form.get('movilidad', '').strip()
    estado_mental = request.form.get('estado_mental', '').strip()

    # Resto de campos
    nacionalidad = request.form.get('pais_nacimiento', '').strip().upper()
    direccion = request.form.get('direccion', '').strip().upper()
    telefono_contacto = request.form.get('telefono', '').strip()
    contacto_emergencia_nombre = request.form.get('nombre_contacto_emergencia', '').strip().upper()
    contacto_emergencia_parentesco = request.form.get('contacto_emergencia_parentesco', '').strip().upper()
    contacto_emergencia_telefono = request.form.get('telefono_emergencia', '').strip()

    # ———————— Validación: todos los ENUM deben tener valor ————————
    if not genero or not estado_civil or not movilidad or not estado_mental:
        mensaje = 'faltan_campos'
        return render_template(
            'modulos/clientes/create.html',
            mensaje=mensaje,
            nombre=nombre,
            apellido1=apellido1,
            apellido2=apellido2,
            cedula=cedula,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero,
            estado_civil=estado_civil,
            pais_nacimiento=nacionalidad,
            direccion=direccion,
            telefono=telefono_contacto,
            nombre_contacto_emergencia=contacto_emergencia_nombre,
            contacto_emergencia_parentesco=contacto_emergencia_parentesco,
            telefono_emergencia=contacto_emergencia_telefono,
            movilidad=movilidad,
            estado_mental=estado_mental
        )

    # ———————— Preparar INSERT del residente ————————
    sql = """
    INSERT INTO residentes(
      nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero,
      estado_civil, nacionalidad, direccion, telefono_contacto,
      contacto_emergencia_nombre, contacto_emergencia_parentesco, contacto_emergencia_telefono,
      movilidad, estado_mental
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    data = (
        nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil,
        nacionalidad, direccion, telefono_contacto,
        contacto_emergencia_nombre, contacto_emergencia_parentesco, contacto_emergencia_telefono,
        movilidad, estado_mental
    )

    cursor = db.database.cursor()

    # ———————— Verificar si la cédula ya existe ————————
    cursor.execute("SELECT cedula FROM residentes WHERE cedula = %s", (cedula,))
    existente = cursor.fetchone()
    if existente:
        cursor.close()
        mensaje = 'existe'
        return render_template(
            'modulos/clientes/create.html',
            mensaje=mensaje,
            cedula=cedula
        )

    # ———————— Intentar INSERT/commit ————————
    try:
        # Insertar residente
        cursor.execute(sql, data)
        residente_id = cursor.lastrowid  # Obtener el ID del residente recién insertado
        
        # ========== LOGS ESPECÍFICOS PARA BITÁCORA ==========
        print("\n" + "="*50)
        print("📋 PROCESO DE INSERCIÓN EN BITÁCORA")
        print("="*50)
        
        # ———————— Registrar en bitácora de pacientes ————————
        # ✅ CORREGIDO: Usar current_user.id en lugar de session.get()
        personal_id = current_user.id
        print(f"1️⃣ Personal ID desde current_user: {personal_id}")
        print(f"   - Usuario: {current_user.nombre}")
        print(f"   - Rol: {current_user.rol}")
        
        if not personal_id:
            print("❌ ERROR: No hay personal_id (usuario no autenticado)")
            print("   - Esto no debería pasar porque la ruta tiene @login_required")
        else:
            # Verificar que el personal_id existe en la tabla usuarios
            cursor.execute("SELECT id, nombre FROM usuarios WHERE id = %s", (personal_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                print(f"❌ ERROR: No existe usuario con ID {personal_id} en tabla 'usuarios'")
                print("   - Verificar que el ID sea correcto")
                print("   - La bitácora NO se registrará")
            else:
                print(f"2️⃣ Usuario encontrado: {usuario[1]} (ID: {usuario[0]})")
                
                # Descripción detallada del nuevo residente
                descripcion_bitacora = f"""
Registro de Nuevo Ingreso
"""
                
                sql_bitacora = """
                INSERT INTO bitacora_pacientes (
                    residente_id, 
                    tipo, 
                    descripcion, 
                    personal_id, 
                    estado
                ) VALUES (%s, %s, %s, %s, %s)
                """
                
                datos_bitacora = (
                    residente_id,
                    'observacion',
                    descripcion_bitacora.strip(),
                    personal_id,
                    'activo'
                )
                
                print(f"3️⃣ Datos a insertar en bitácora:")
                print(f"   - residente_id: {residente_id}")
                print(f"   - tipo: observacion")
                print(f"   - personal_id: {personal_id}")
                print(f"   - estado: activo")
                print(f"   - descripción: {len(descripcion_bitacora)} caracteres")
                
                try:
                    cursor.execute(sql_bitacora, datos_bitacora)
                    filas_afectadas = cursor.rowcount
                    print(f"4️⃣ Filas afectadas en bitácora: {filas_afectadas}")
                    
                    if filas_afectadas > 0:
                        print(f"✅ INSERCIÓN EN BITÁCORA EXITOSA")
                        # Obtener el ID del registro insertado
                        bitacora_id = cursor.lastrowid
                        print(f"   - ID del registro en bitácora: {bitacora_id}")
                    else:
                        print(f"❌ INSERCIÓN EN BITÁCORA FALLÓ (0 filas afectadas)")
                        
                except mysql.connector.Error as err_bitacora:
                    print(f"❌ ERROR EN INSERCIÓN DE BITÁCORA:")
                    print(f"   - Código: {err_bitacora.errno}")
                    print(f"   - Mensaje: {err_bitacora.msg}")
                    print(f"   - SQLSTATE: {err_bitacora.sqlstate}")
                    # No hacer rollback aquí, solo registrar el error
        
        print("="*50 + "\n")
        
        db.database.commit()
        
    except mysql.connector.Error as err:
        db.database.rollback()
        cursor.close()
        mensaje = 'error_insercion'
        return render_template(
            'modulos/clientes/create.html',
            mensaje=mensaje,
            error_detalle=err.msg,
            cedula=cedula
        )
    finally:
        cursor.close()

    # ———————— Éxito ————————
    mensaje = 'insertado'
    
    # Pasar datos del nuevo residente para mostrarlos en el modal
    return render_template(
        'modulos/clientes/create.html', 
        mensaje=mensaje, 
        cedula=cedula,
        nuevo_residente={
            'id': residente_id,
            'nombre': nombre,
            'apellido1': apellido1,
            'cedula': cedula
        }
    )

from flask import request, jsonify

@app.route('/historial_medico/<int:id>/editar', methods=['POST'])
def editar_historial(id):
    # Validar y actualizar en base a request.form
    fecha = request.form.get('fecha')
    diagnostico = request.form.get('diagnostico')
    observaciones = request.form.get('observaciones')

    # Aquí actualizas la base de datos y guardas los cambios

    # Simular respuesta exitosa
    return jsonify({
        'success': True,
        'id': id,
        'fecha': datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y'),  # para mostrar en la tabla
        'fecha_backend': fecha,  # para rellenar input date
        'diagnostico': diagnostico,
        'observaciones': observaciones
    })



@app.route('/modulos/clientes/create/edit/<string:id>', methods=['POST'])
@login_required
@role_required('administrador', 'medico', 'asistente_administrativo') 
def btn_cliente_editar_guardar(id):
    # Obtener datos del formulario
    nombre = request.form.get('nombre', '').strip().upper()
    apellido1 = request.form.get('apellido1', '').strip().upper()
    apellido2 = request.form.get('apellido2', '').strip().upper()
    cedula = request.form.get('cedula', '').strip()
    fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
    genero = request.form.get('genero', '').strip().upper()
    estado_civil = request.form.get('estado_civil', '').strip().upper()
    nacionalidad = request.form.get('pais_nacimiento', '').strip().upper()
    direccion = request.form.get('direccion', '').strip().upper()
    telefono_contacto = request.form.get('telefono', '').strip()
    contacto_emergencia_nombre = request.form.get('nombre_contacto_emergencia', '').strip().upper()
    contacto_emergencia_parentesco = request.form.get('contacto_emergencia_parentesco', '').strip().upper()
    contacto_emergencia_telefono = request.form.get('telefono_emergencia', '').strip()
    condiciones_medicas = request.form.get('condiciones_medicas', '').strip().upper()
    medicamentos_actuales = request.form.get('medicamentos', '').strip().upper()
    movilidad = request.form.get('movilidad', '').strip().upper()
    estado_mental = request.form.get('estado_mental', '').strip()

   

    data = (
        nombre, apellido1, apellido2, cedula, fecha_nacimiento, genero, estado_civil, nacionalidad,
        direccion, telefono_contacto, contacto_emergencia_nombre, contacto_emergencia_parentesco,
        contacto_emergencia_telefono, condiciones_medicas, medicamentos_actuales, movilidad,
        estado_mental, id
    )

    cursor = db.database.cursor()

    # Validar cédula duplicada (excluyendo el mismo registro)
    cursor.execute("SELECT id FROM residentes WHERE cedula = %s AND id != %s", (cedula, id))
    existente = cursor.fetchone()
        
    if existente:
        mensaje = 'existe'
        return render_template('modulos/clientes/create.html', mensaje=mensaje, cedula=cedula)

    # Intentar guardar cambios
    sql = """
        UPDATE residentes
        SET nombre = %s,
            apellido1 = %s,
            apellido2 = %s,
            cedula = %s,
            fecha_nacimiento = %s,
            genero = %s,
            estado_civil = %s,
            nacionalidad = %s,
            direccion = %s,
            telefono_contacto = %s,
            contacto_emergencia_nombre = %s,
            contacto_emergencia_parentesco = %s,
            contacto_emergencia_telefono = %s,
            condiciones_medicas = %s,
            medicamentos_actuales = %s,
            movilidad = %s,
            estado_mental = %s
        WHERE id = %s
    """
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    mensaje = 'no_existe'

    return redirect(f'/ver_info/{id}')






##busqueda por dato ingresado

@app.route('/buscar')
@login_required
def buscar():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    query = query.lower()
    like_query = f"%{query}%"
    sql = """
        SELECT id, cedula, nombre, apellido1, apellido2, nacionalidad, telefono_contacto, direccion, activo
        FROM residentes
        WHERE 
            LOWER(nombre) LIKE %s OR
            LOWER(apellido1) LIKE %s OR
            LOWER(apellido2) LIKE %s OR
            LOWER(nacionalidad) LIKE %s OR
            LOWER(telefono_contacto) LIKE %s OR
            cedula LIKE %s
        LIMIT 20
    """
    cursor = db.database.cursor()
    try:
        cursor.execute(sql, (like_query,) * 6)
        datos = cursor.fetchall()
        columnas = [col[0] for col in cursor.description]
        arreglo = [dict(zip(columnas, registro)) for registro in datos]
    finally:
        cursor.close()

    return jsonify(arreglo)






@app.route('/ver_info/<string:id>', methods=['GET'])
@login_required
@role_required('administrador', 'medico', 'enfermeria', 'asistente_administrativo')
def index_ver_info(id):
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM residentes WHERE id = %s", (id,))
    residente = cursor.fetchone()
    
    if not residente:
        flash("Residente no encontrado", "danger")
        return redirect(url_for('index_residentes'))
    
    cursor.close()
    
    # Para compatibilidad, también pasamos como arreglo
    arreglo = [residente] if residente else []
    
    return render_template('/modulos/clientes/ver_info.html', 
                          residente=residente,
                          arreglo=arreglo)

@app.route('/toggle_estado/<int:residente_id>', methods=['POST'])
@login_required
@role_required('administrador', 'asistente_administrativo')
def toggle_estado_residente(residente_id):
    data = request.get_json()
    nuevo_estado = data.get('estado')

    if nuevo_estado is None:
        return jsonify({'success': False, 'error': 'Estado no proporcionado'}), 400

    estado_db = 1 if nuevo_estado in [True, 'true', 'activo', 1] else 0

    cursor = db.database.cursor()
    try:
        cursor.execute("UPDATE residentes SET activo = %s WHERE id = %s", (estado_db, residente_id))
        db.database.commit()
        return jsonify({'success': True, 'estado': estado_db})
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()



# MODULO HISTORIAL MEDICO



# Mostrar historial médico
@app.route('/historial_medico/<int:id>')
@login_required
def historial_medico(id):
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM historial_medico WHERE residente_id = %s", (id,))
    historial = cursor.fetchall()
    cursor.execute("""
    SELECT CONCAT(nombre, ' ', apellido1, ' ', apellido2) AS nombre_completo 
    FROM residentes 
    WHERE id = %s
""", (id,))
    residente = cursor.fetchone() 
    cursor.close()
    return render_template('/modulos/clientes/historial_medico.html', historial=historial, residente=residente ,residente_id=id)


@app.route('/medicacion/<int:residente_id>')
@login_required
def medicacion(residente_id):
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM medicacion
        WHERE residente_id = %s
        ORDER BY fecha_inicio DESC
    """, (residente_id,))
    lista_medicacion = cursor.fetchall()
    cursor.close()

    return render_template(
        'modulos/clientes/medicacion.html',
        medicacion=lista_medicacion,
        residente_id=residente_id
    )



def texto_frecuencia(f):
    mapa = {
        '1xdia': '1 vez al día',
        '2xdia': '2 veces al día',
        '3xdia': '3 veces al día',
        'cada_6h': 'Cada 6 horas',
        'cada_8h': 'Cada 8 horas',
        'cada_12h': 'Cada 12 horas'
    }
    return mapa.get(f, f)

from datetime import datetime, timedelta
def generar_horarios(frecuencia_tipo, hora_inicio):
    base = datetime.strptime(hora_inicio, '%H:%M')
    horas = []

    if frecuencia_tipo == '1xdia':
        horas = [base]
    elif frecuencia_tipo == '2xdia':
        horas = [base, base + timedelta(hours=12)]
    elif frecuencia_tipo == '3xdia':
        horas = [base + timedelta(hours=8*i) for i in range(3)]
    elif frecuencia_tipo == 'cada_6h':
        horas = [base + timedelta(hours=6*i) for i in range(4)]
    elif frecuencia_tipo == 'cada_8h':
        horas = [base + timedelta(hours=8*i) for i in range(3)]
    elif frecuencia_tipo == 'cada_12h':
        horas = [base, base + timedelta(hours=12)]

    return ','.join(h.strftime('%H:%M') for h in horas)


@app.route('/medicacion/nueva/<int:residente_id>', methods=['POST'])
@login_required
@role_required("medico")
def agregar_medicacion(residente_id):

    # 🔐 1. Verificar que sea personal médico
    if current_user.rol != "medico":
        abort(403)

    medicamento = request.form['medicamento']
    dosis = request.form['dosis']
    via = request.form['via_administracion']
    frecuencia_tipo = request.form['frecuencia_tipo']
    frecuencia = texto_frecuencia(frecuencia_tipo)
    modo = request.form['modo_horario']

    if modo == 'automatico':
        hora_inicio = request.form['hora_inicio']
        horarios = generar_horarios(frecuencia_tipo, hora_inicio)
    else:
        horarios = request.form['horarios']
        hora_inicio = None

    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form.get('fecha_fin') or None
    notas = request.form.get('notas')
    creado_por = current_user.id

    cursor = db.database.cursor()

    try:
        # 🟢 INSERT medicación
        cursor.execute("""
            INSERT INTO medicacion
            (residente_id, medicamento, dosis, via_administracion,
             frecuencia, horarios, fecha_inicio, fecha_fin,
             notas, creado_por)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            residente_id, medicamento, dosis, via,
            frecuencia, horarios, fecha_inicio,
            fecha_fin, notas, creado_por
        ))

        medicacion_id = cursor.lastrowid

        # 🟢 Crear registro en bitácora
        descripcion = f"Se prescribió {medicamento} {dosis} vía {via}"

        cursor.execute("""
            INSERT INTO bitacora_pacientes
            (residente_id, tipo, descripcion, personal_id)
            VALUES (%s, 'medicacion', %s, %s)
        """, (
            residente_id,
            descripcion,
            current_user.id
        ))

        db.database.commit()

    except Exception as e:
        db.database.rollback()
        flash("Error al agregar la medicación", "danger")
        return redirect(url_for('medicacion', residente_id=residente_id))

    finally:
        cursor.close()

    flash("Medicamento agregado correctamente", "success")
    return redirect(url_for('medicacion', residente_id=residente_id))





@app.route('/medicacion/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required("administrador")
def eliminar_medicacion(id):
    cursor = db.database.cursor(dictionary=True)

    cursor.execute("SELECT residente_id FROM medicacion WHERE id = %s", (id,))
    registro = cursor.fetchone()

    if not registro:
        cursor.close()
        flash('Registro no encontrado.', 'danger')
        return redirect(url_for('dashboard'))

    residente_id = registro['residente_id']

    cursor.execute("DELETE FROM medicacion WHERE id = %s", (id,))
    db.database.commit()
    cursor.close()

    flash('Medicamento eliminado correctamente.', 'success')
    return redirect(url_for('medicacion', residente_id=residente_id))


@app.route('/medicaciones/tratamientos-activos')
@login_required
def tratamientos_activos():
    cursor = db.database.cursor(dictionary=True)

    sql = """
        SELECT
    r.nombre AS residente,
    m.medicamento,
    m.dosis,
    m.via_administracion,
    m.frecuencia,
    m.horarios,
    m.fecha_inicio,
    m.fecha_fin,
    u.nombre AS medico,
    m.estado
FROM medicacion m
INNER JOIN residentes r ON r.id = m.residente_id
INNER JOIN usuarios u ON u.id = m.creado_por
WHERE m.estado = 'activa'
  AND m.fecha_inicio <= CURDATE()
  AND (m.fecha_fin IS NULL OR m.fecha_fin >= CURDATE())
ORDER BY r.nombre, m.medicamento;

    """

    cursor.execute(sql)
    tratamientos = cursor.fetchall()
    cursor.close()

    return render_template(
        'modulos/clientes/tratamientos_activos.html',
        tratamientos=tratamientos
    )


from datetime import datetime, date

def generar_tomas_diarias():
    """
    Genera SOLO las administraciones para HOY
    basándose en la medicación activa
    """
    cursor = db.database.cursor(dictionary=True)
    hoy = date.today()
    
    try:
        # 1. Obtener TODAS las medicaciones activas que aplican HOY
        cursor.execute("""
            SELECT 
                id, 
                horarios,
                fecha_inicio,
                fecha_fin,
                frecuencia
            FROM medicacion 
            WHERE estado = 'activa'
              AND fecha_inicio <= %s
              AND (fecha_fin IS NULL OR fecha_fin >= %s)
        """, (hoy, hoy))
        
        medicaciones = cursor.fetchall()
        
        registros_generados = 0
        
        for med in medicaciones:
            if not med['horarios']:
                continue  # Si no tiene horarios, no podemos generar nada
            
            # Separar horarios: "08:00,14:00,20:00" → ["08:00", "14:00", "20:00"]
            horarios = [h.strip() for h in med['horarios'].split(',') if h.strip()]
            
            for hora in horarios:
                # Verificar si YA EXISTE una administración para hoy a esta hora
                cursor.execute("""
                    SELECT id 
                    FROM administraciones_medicacion
                    WHERE medicacion_id = %s
                      AND fecha = %s
                      AND hora_programada = %s
                """, (med['id'], hoy, hora))
                
                if cursor.fetchone():
                    continue  # Ya existe, no duplicar
                
                # Crear nueva administración
                cursor.execute("""
                    INSERT INTO administraciones_medicacion
                    (medicacion_id, fecha, hora_programada, estado)
                    VALUES (%s, %s, %s, 'pendiente')
                """, (med['id'], hoy, hora))
                
                registros_generados += 1
        
        db.database.commit()
        print(f"✓ Generadas {registros_generados} administraciones para {hoy}")
        return registros_generados
        
    except Exception as e:
        db.database.rollback()
        print(f"✗ Error generando tomas: {e}")
        return 0
        
    finally:
        cursor.close()



def formatear_hora_12h(hora):
    if not hora:
        return None

    if isinstance(hora, time):
        return hora.strftime('%I:%M %p')

    if isinstance(hora, datetime):
        return hora.strftime('%I:%M %p')

    # fallback por si MySQL devuelve string "HH:MM:SS"
    try:
        return datetime.strptime(str(hora), '%H:%M:%S').strftime('%I:%M %p')
    except Exception:
        return str(hora)



@app.route('/control-diario-medicacion')
@login_required
def control_diario():
    if current_user.rol not in ['enfermeria', 'farmacia', 'medico', 'personal_salud', 'administrador']:
        flash("No tienes permisos para acceder a esta sección", "danger")
        return redirect(url_for('index_admin'))

    generar_tomas_diarias()

    cursor = db.database.cursor(dictionary=True)

    try:
        hoy = date.today()

        # 1. Marcar tomas atrasadas
        cursor.execute("""
            UPDATE administraciones_medicacion
            SET estado = 'atrasada'
            WHERE fecha = %s 
              AND estado = 'pendiente'
              AND TIMESTAMPDIFF(
                    MINUTE, 
                    CONCAT(fecha, ' ', hora_programada), 
                    NOW()
              ) > 30
        """, (hoy,))
        db.database.commit()

        # 2. Obtener tomas del día
        cursor.execute("""
            SELECT
                a.id,
                a.fecha,
                r.nombre AS residente,
                r.id AS residente_id,
                m.medicamento,
                m.dosis,
                m.via_administracion,
                m.frecuencia,
                a.hora_programada,
                a.estado,
                a.hora_administrada,
                a.observaciones,
                a.administrado_por,
                u.nombre AS administrador_nombre,
                TIMESTAMPDIFF(
                    MINUTE, 
                    CONCAT(a.fecha, ' ', a.hora_programada), 
                    NOW()
                ) AS minutos_atraso
            FROM administraciones_medicacion a
            JOIN medicacion m ON m.id = a.medicacion_id
            JOIN residentes r ON r.id = m.residente_id
            LEFT JOIN usuarios u ON u.id = a.administrado_por
            WHERE a.fecha = %s
            ORDER BY 
                CASE a.estado 
                    WHEN 'pendiente' THEN 1
                    WHEN 'atrasada' THEN 2
                    WHEN 'administrada' THEN 3
                    WHEN 'omitida' THEN 4
                    WHEN 'rechazada' THEN 5
                    ELSE 6
                END,
                a.hora_programada,
                r.nombre
        """, (hoy,))

        tomas = cursor.fetchall()
        print(f"tomas {tomas} ")
        # 👉 FORMATEO DE HORAS A 12H
        for toma in tomas:
            toma['hora_programada_12h'] = formatear_hora_12h(toma['hora_programada'])
            toma['hora_administrada_12h'] = formatear_hora_12h(
                toma.get('hora_administrada')
            )

        # 3. Estadísticas
        cursor.execute("""
            SELECT 
                COUNT(*) AS total,
                SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) AS pendientes,
                SUM(CASE WHEN estado = 'atrasada' THEN 1 ELSE 0 END) AS atrasadas,
                SUM(CASE WHEN estado = 'administrada' THEN 1 ELSE 0 END) AS administradas,
                SUM(CASE WHEN estado = 'omitida' THEN 1 ELSE 0 END) AS omitidas,
                SUM(CASE WHEN estado = 'rechazada' THEN 1 ELSE 0 END) AS rechazadas
            FROM administraciones_medicacion
            WHERE fecha = %s
        """, (hoy,))

        stats = cursor.fetchone()

        return render_template(
            'modulos/clientes/control_diario.html',
            tomas=tomas,
            stats=stats,
            hoy=hoy.strftime('%d/%m/%Y'),
            hora_actual=datetime.now().strftime('%I:%M %p'),
            ahora=datetime.now()
        )

    except Exception as e:
        db.database.rollback()
        flash(f"Error al cargar el control diario: {str(e)}", "danger")
        return redirect(url_for('index_admin'))

    finally:
        cursor.close()


#****bitacora**

# BITÁCORA DE PACIENTES


@app.route('/bitacora/<int:residente_id>')
@login_required
def bitacora_paciente(residente_id):
    """Vista principal de la bitácora de un paciente"""
    cursor = db.database.cursor(dictionary=True)
    
    # Obtener información del residente
    cursor.execute("""
        SELECT id, CONCAT(nombre, ' ', apellido1, ' ', apellido2) as nombre_completo 
        FROM residentes 
        WHERE id = %s
    """, (residente_id,))
    residente = cursor.fetchone()
    
    if not residente:
        flash("Residente no encontrado", "danger")
        return redirect(url_for('index_admin'))
    
    # Obtener registros de la bitácora
    cursor.execute("""
        SELECT b.*, u.nombre as personal_nombre
        FROM bitacora_pacientes b
        LEFT JOIN usuarios u ON b.personal_id = u.id
        WHERE b.residente_id = %s AND b.estado = 'activo'
        ORDER BY b.fecha_hora DESC
        LIMIT 50
    """, (residente_id,))
    
    registros = cursor.fetchall()
    cursor.close()
    
    # Formatear fechas en Python
    for registro in registros:
        if registro['fecha_hora']:
            try:
                # Convertir a objeto datetime si es string
                if isinstance(registro['fecha_hora'], str):
                    fecha_obj = datetime.strptime(registro['fecha_hora'], '%Y-%m-%d %H:%M:%S')
                else:
                    fecha_obj = registro['fecha_hora']
                
                registro['fecha_formateada'] = fecha_obj.strftime('%d/%m/%Y %H:%M')
            except Exception as e:
                registro['fecha_formateada'] = str(registro['fecha_hora'])
        else:
            registro['fecha_formateada'] = 'N/A'
    
    return render_template(
        'modulos/clientes/bitacora.html',
        residente=residente,
        registros=registros,
        residente_id=residente_id
    )

@app.route('/bitacora/buscar-paciente', methods=['GET', 'POST'])
@login_required
def buscar_paciente_bitacora():
    """Buscador de pacientes específico para bitácora"""
    try:
        cursor = db.database.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, cedula, nombre, apellido1, apellido2, 
                   nacionalidad, telefono_contacto, direccion, activo,
                   CONCAT(nombre, ' ', apellido1, ' ', COALESCE(apellido2, '')) as nombre_completo
            FROM residentes 
            ORDER BY nombre, apellido1
            LIMIT 20
        """)
        residentes = cursor.fetchall()
    except Exception as e:
        print("ERROR EN BUSCAR PACIENTES BITÁCORA:", e)
        residentes = []
    finally:
        cursor.close()

    return render_template(
        'modulos/clientes/buscar_paciente_bitacora.html', 
        residentes=residentes
    )



@app.route('/bitacora/agregar/<int:residente_id>', methods=['POST'])
@login_required
def agregar_bitacora(residente_id):
    """Agrega un nuevo registro a la bitácora"""
    tipo = request.form.get('tipo')
    descripcion = request.form.get('descripcion', '').strip()
    hora_registro = request.form.get('hora_registro')  # Opcional, si quieren especificar hora
    
    if not tipo or not descripcion:
        flash("Tipo y descripción son obligatorios", "danger")
        return redirect(url_for('bitacora_paciente', residente_id=residente_id))
    
    cursor = db.database.cursor()
    
    try:
        if hora_registro:
            # Si se especifica hora manual
            sql = """
                INSERT INTO bitacora_pacientes 
                (residente_id, tipo, descripcion, personal_id, fecha_hora)
                VALUES (%s, %s, %s, %s, %s)
            """
            fecha_hora = datetime.now().strftime('%Y-%m-%d ') + hora_registro
            cursor.execute(sql, (residente_id, tipo, descripcion, current_user.id, fecha_hora))
        else:
            # Usar fecha/hora actual
            sql = """
                INSERT INTO bitacora_pacientes 
                (residente_id, tipo, descripcion, personal_id)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (residente_id, tipo, descripcion, current_user.id))
        
        db.database.commit()
        
        # Si es tipo medicación, relacionar con medicación pendiente
        if tipo == 'medicacion':
            medicacion_id = request.form.get('medicacion_id')
            if medicacion_id:
                cursor.execute("""
                    INSERT INTO bitacora_medicacion (bitacora_id, medicacion_id)
                    VALUES (%s, %s)
                """, (cursor.lastrowid, medicacion_id))
                db.database.commit()
        
        flash("Registro agregado correctamente", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al agregar registro: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('bitacora_paciente', residente_id=residente_id))

@app.route('/bitacora/filtrar/<int:residente_id>', methods=['POST'])
@login_required
def filtrar_bitacora(residente_id):
    """Filtra registros de la bitácora"""
    tipo = request.form.get('filtro_tipo', '')
    fecha_inicio = request.form.get('fecha_inicio', '')
    fecha_fin = request.form.get('fecha_fin', '')
    
    cursor = db.database.cursor(dictionary=True)
    
    query = """
        SELECT b.*, 
               u.nombre as personal_nombre,
               DATE_FORMAT(b.fecha_hora, '%%d/%%m/%%Y %%H:%%i') as fecha_formateada
        FROM bitacora_pacientes b
        LEFT JOIN usuarios u ON b.personal_id = u.id
        WHERE b.residente_id = %s AND b.estado = 'activo'
    """
    params = [residente_id]
    
    if tipo:
        query += " AND b.tipo = %s"
        params.append(tipo)
    
    if fecha_inicio:
        query += " AND DATE(b.fecha_hora) >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        query += " AND DATE(b.fecha_hora) <= %s"
        params.append(fecha_fin)
    
    query += " ORDER BY b.fecha_hora DESC LIMIT 100"
    
    cursor.execute(query, tuple(params))
    registros = cursor.fetchall()
    
    # Obtener información del residente
    cursor.execute("""
        SELECT id, CONCAT(nombre, ' ', apellido1, ' ', apellido2) as nombre_completo 
        FROM residentes 
        WHERE id = %s
    """, (residente_id,))
    residente = cursor.fetchone()
    
    cursor.close()
    
    return render_template(
        'modulos/clientes/bitacora.html',
        residente=residente,
        registros=registros,
        residente_id=residente_id,
        filtro_tipo=tipo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@app.route('/bitacora/editar/<int:registro_id>', methods=['POST'])
@login_required
def editar_bitacora(registro_id):      
    # Verificar permisos
    if current_user.rol not in ['administrador']:
        flash("No tienes permisos para esta acción", "danger")
        residente_id = request.form.get('residente_id')
        if residente_id:
            return redirect(url_for('bitacora_paciente', residente_id=residente_id))
        return redirect(url_for('index_admin'))
    
    # Obtener datos del formulario
    descripcion = request.form.get('descripcion', '').strip()
    justificacion = request.form.get('justificacion', '').strip()
    residente_id = request.form.get('residente_id')
    
    # Validar residente_id
    if not residente_id:
        flash("Error: ID de residente no proporcionado", "danger")
        return redirect(url_for('index_admin'))
    
    # Validar descripción
    if not descripcion:
        flash("La descripción no puede estar vacía", "danger")
        return redirect(url_for('bitacora_paciente', residente_id=residente_id))
    
    # Validar justificación
    if not justificacion:
        flash("Debe proporcionar una justificación para la modificación", "warning")
        return redirect(url_for('bitacora_paciente', residente_id=residente_id))
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener el registro actual
        cursor.execute("SELECT * FROM bitacora_pacientes WHERE id = %s", (registro_id,))
        registro = cursor.fetchone()
        
        if not registro:
            flash("Registro no encontrado", "danger")
            return redirect(url_for('bitacora_paciente', residente_id=residente_id))
        
        # Verificar que el registro pertenezca al residente
        if str(registro['residente_id']) != str(residente_id):
            flash("El registro no pertenece al residente especificado", "danger")
            return redirect(url_for('bitacora_paciente', residente_id=residente_id))
        
        # 🔴 ACTUALIZACIÓN CORREGIDA para tu estructura de tabla
        # SOLO actualizar el registro existente (no crear uno nuevo)
        cursor.execute("""
            UPDATE bitacora_pacientes 
            SET descripcion = %s,
                justificacion = %s,
                modificado_por = %s,
                estado = 'modificado'
            WHERE id = %s
        """, (descripcion, justificacion, current_user.id, registro_id))
        
        db.database.commit()
        flash("Registro actualizado correctamente", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")
        print(f"Error en editar_bitacora: {str(e)}")
    finally:
        cursor.close()
    
    return redirect(url_for('bitacora_paciente', residente_id=residente_id))

@app.route('/bitacora/reporte-diario')
@login_required
@role_required('administrador', 'supervisor', 'medico')
def reporte_bitacora_diario():
    """Genera reporte diario de bitácoras"""
    cursor = db.database.cursor(dictionary=True)
    
    fecha = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    
    # Estadísticas por tipo
    cursor.execute("""
        SELECT 
            b.tipo,
            COUNT(*) as cantidad,
            GROUP_CONCAT(DISTINCT r.nombre SEPARATOR ', ') as residentes
        FROM bitacora_pacientes b
        JOIN residentes r ON b.residente_id = r.id
        WHERE DATE(b.fecha_hora) = %s AND b.estado = 'activo'
        GROUP BY b.tipo
        ORDER BY cantidad DESC
    """, (fecha,))
    
    estadisticas = cursor.fetchall()
    
    # Últimos registros del día
    cursor.execute("""
        SELECT 
            b.*,
            r.nombre as residente_nombre,
            u.nombre as personal_nombre,
            DATE_FORMAT(b.fecha_hora, '%%H:%%i') as hora
        FROM bitacora_pacientes b
        JOIN residentes r ON b.residente_id = r.id
        JOIN usuarios u ON b.personal_id = u.id
        WHERE DATE(b.fecha_hora) = %s AND b.estado = 'activo'
        ORDER BY b.fecha_hora DESC
        LIMIT 50
    """, (fecha,))
    
    registros = cursor.fetchall()
    cursor.close()
    
    return render_template(
        'modulos/reportes/bitacora_diaria.html',
        estadisticas=estadisticas,
        registros=registros,
        fecha=fecha,
        fecha_formateada=datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y') if fecha else ''
    )

# Ruta para obtener medicaciones pendientes para autocompletar
@app.route('/bitacora/medicaciones-pendientes/<int:residente_id>')
@login_required
def medicaciones_pendientes(residente_id):
    """Devuelve medicaciones pendientes para autocompletar en bitácora"""
    cursor = db.database.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT m.id, m.medicamento, m.dosis, m.via_administracion
        FROM medicacion m
        WHERE m.residente_id = %s 
          AND m.estado = 'activa'
          AND (m.fecha_fin IS NULL OR m.fecha_fin >= CURDATE())
        ORDER BY m.medicamento
    """, (residente_id,))
    
    medicaciones = cursor.fetchall()
    cursor.close()
    
    return jsonify(medicaciones)

# Integración con control diario de medicación
@app.route('/bitacora/registrar-medicacion-automatica/<int:admin_id>', methods=['POST'])
@login_required
def registrar_medicacion_automatica(admin_id):
    """Registra automáticamente en bitácora cuando se administra medicación"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener datos de la administración
        cursor.execute("""
            SELECT a.*, m.medicamento, m.dosis, m.via_administracion, r.id as residente_id
            FROM administraciones_medicacion a
            JOIN medicacion m ON m.id = a.medicacion_id
            JOIN residentes r ON m.residente_id = r.id
            WHERE a.id = %s
        """, (admin_id,))
        
        admin = cursor.fetchone()
        
        if not admin:
            return jsonify({'success': False, 'error': 'Administración no encontrada'})
        
        # Crear registro en bitácora
        descripcion = f"{admin['medicamento']} {admin['dosis']} via {admin['via_administracion']}"
        
        cursor.execute("""
            INSERT INTO bitacora_pacientes 
            (residente_id, tipo, descripcion, personal_id)
            VALUES (%s, 'medicacion', %s, %s)
        """, (admin['residente_id'], descripcion, current_user.id))
        
        bitacora_id = cursor.lastrowid
        
        # Relacionar con la medicación
        cursor.execute("""
            INSERT INTO bitacora_medicacion (bitacora_id, medicacion_id, administracion_id)
            VALUES (%s, %s, %s)
        """, (bitacora_id, admin['medicacion_id'], admin_id))
        
        db.database.commit()
        
        return jsonify({'success': True, 'bitacora_id': bitacora_id})
        
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cursor.close()

#***fin bitacora**


@app.route('/medicacion/administrar/<int:admin_id>', methods=['POST'])
@login_required
def administrar_medicacion(admin_id):
    if current_user.rol not in ['enfermeria','farmacia', 'medico', 'personal_salud', 'administrador']:
        flash("No tienes permisos para esta acción", "danger")
        return redirect('/control-diario-medicacion')
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener datos básicos
        cursor.execute("""
            SELECT a.*, 
                   m.medicamento, m.dosis, m.via_administracion, 
                   m.residente_id, r.nombre as residente_nombre
            FROM administraciones_medicacion a
            JOIN medicacion m ON m.id = a.medicacion_id
            JOIN residentes r ON r.id = m.residente_id
            WHERE a.id = %s
        """, (admin_id,))
        
        admin = cursor.fetchone()
        
        if not admin:
            flash('Administración no encontrada', "danger")
            return redirect('/control-diario-medicacion')
        
        if admin['estado'] == 'administrada':
            flash('Esta medicación ya fue administrada', "warning")
            return redirect('/control-diario-medicacion')
        
        observaciones = request.form.get('observaciones', '')
        
        # 1. Actualizar la administración
        cursor.execute("""
            UPDATE administraciones_medicacion
            SET estado = 'administrada',
                hora_administrada = CURTIME(),
                administrado_por = %s,
                observaciones = %s
            WHERE id = %s
        """, (current_user.id, observaciones, admin_id))
        
        # 2. Crear registro en bitácora
        # CORRECCIÓN: Manejar timedelta correctamente
        hora_programada = admin['hora_programada']
        
        # Convertir timedelta a string de hora
        if isinstance(hora_programada, timedelta):
            # timedelta a string HH:MM
            total_seconds = int(hora_programada.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            hora_programada_str = f"{hours:02d}:{minutes:02d}"
        elif hora_programada:
            # Si ya es datetime o time
            try:
                hora_programada_str = hora_programada.strftime('%H:%M')
            except:
                hora_programada_str = str(hora_programada)
        else:
            hora_programada_str = 'N/A'
        
        descripcion_bitacora = f"""
Medicación administrada: {admin['medicamento']} {admin['dosis']}
Vía: {admin['via_administracion']}
Hora programada: {hora_programada_str}
Hora administrada: {datetime.now().strftime('%H:%M')}
Observaciones: {observaciones if observaciones else 'Ninguna'}
        """.strip()
        
        cursor.execute("""
            INSERT INTO bitacora_pacientes 
            (residente_id, tipo, descripcion, personal_id)
            VALUES (%s, 'medicacion', %s, %s)
        """, (admin['residente_id'], descripcion_bitacora, current_user.id))
        
        db.database.commit()
        
        flash(f'✅ {admin["medicamento"]} administrado a {admin["residente_nombre"]}', "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f'Error al registrar: {str(e)}', "danger")
        print(f"Error administrar_medicacion: {e}")
        
    finally:
        cursor.close()
    
    return redirect('/control-diario-medicacion')



@app.route('/medicacion/omitir/<int:admin_id>', methods=['POST'])
@login_required
def omitir_medicacion(admin_id):
    if current_user.rol not in ['enfermeria', 'medico', 'personal_salud', 'administrador']:
        flash("No tienes permisos para esta acción", "danger")
        return redirect('/control-diario-medicacion')
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener datos
        cursor.execute("""
            SELECT a.*, m.medicamento, m.dosis, m.residente_id, 
                   r.nombre as residente_nombre
            FROM administraciones_medicacion a
            JOIN medicacion m ON m.id = a.medicacion_id
            JOIN residentes r ON r.id = m.residente_id
            WHERE a.id = %s
        """, (admin_id,))
        
        admin = cursor.fetchone()
        
        if not admin:
            flash('Administración no encontrada', 'danger')
            return redirect('/control-diario-medicacion')
        
        motivo = request.form.get('motivo', 'Sin motivo especificado')
        
        # 1. Actualizar administración
        cursor.execute("""
            UPDATE administraciones_medicacion
            SET estado = 'omitida',
                observaciones = CONCAT(
                    COALESCE(observaciones, ''), 
                    ' | OMITIDA: ', %s,
                    ' - Por: ', %s
                )
            WHERE id = %s AND estado IN ('pendiente', 'atrasada')
        """, (motivo, current_user.nombre, admin_id))
        
        if cursor.rowcount == 0:
            flash('No se pudo omitir (ya administrada)', 'danger')
            return redirect('/control-diario-medicacion')
        
        # 2. Crear registro en bitácora
        # CORRECCIÓN: Manejar timedelta
        hora_programada = admin['hora_programada']
        
        if isinstance(hora_programada, timedelta):
            total_seconds = int(hora_programada.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            hora_programada_str = f"{hours:02d}:{minutes:02d}"
        elif hora_programada:
            try:
                hora_programada_str = hora_programada.strftime('%H:%M')
            except:
                hora_programada_str = str(hora_programada)
        else:
            hora_programada_str = 'N/A'
        
        descripcion_bitacora = f"""
Medicación omitida: {admin['medicamento']} {admin['dosis']}
Hora programada: {hora_programada_str}
Motivo: {motivo}
Registrado por: {current_user.nombre}
        """.strip()
        
        cursor.execute("""
            INSERT INTO bitacora_pacientes 
            (residente_id, tipo, descripcion, personal_id)
            VALUES (%s, 'incidente', %s, %s)
        """, (admin['residente_id'], descripcion_bitacora, current_user.id))
        
        db.database.commit()
        
        flash(f'⚠️ {admin["medicamento"]} omitido para {admin["residente_nombre"]}', 'warning')
            
    except Exception as e:
        db.database.rollback()
        flash(f'Error: {str(e)}', 'danger')
        print(f"Error omitir_medicacion: {e}")
        
    finally:
        cursor.close()
    
    return redirect('/control-diario-medicacion')


    


@app.route('/historial_medico/<int:registro_id>/editar', methods=['POST'])
def editar_registro_medico(registro_id):
    # Verificar si es una petición AJAX
    if not request.is_xhr and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({'error': 'Acceso no permitido'}), 403
    
    # Verificar permisos de usuario
    if current_user.rol not in ['administrador']:
        return jsonify({'error': 'No tienes permisos para esta acción'}), 403
    
    # Obtener el registro médico
    registro = RegistroMedico.query.get_or_404(registro_id)
    
    # Aquí continuaría el resto de tu lógica para editar el registro
    # ...
    try:
        fecha = request.form['fecha']
        diagnostico = request.form['diagnostico']
        observaciones = request.form.get('observaciones', '')

        registro.fecha = datetime.strptime(fecha, '')
        registro.diagnostico = diagnostico
        registro.observaciones = observaciones

        db.session.commit()

        return jsonify({
            'success': True,
            'id': registro.id,
            'fecha': registro.fecha.strftime('%d/%m/%Y'),
            'fechaISO': registro.fecha.strftime('%Y-%m-%d'),
            'diagnostico': registro.diagnostico,
            'observaciones': registro.observaciones
        })
    except Exception as e:
        return jsonify({'error': 'No se pudo actualizar el registro'}), 400





@app.route('/historial_medico/<int:residente_id>/nuevo', methods=['POST'])
@login_required
def agregar_historial_medico(residente_id):
    fecha = request.form.get('fecha')
    diagnostico = request.form.get('diagnostico', '').strip()
    observaciones = request.form.get('observaciones', '').strip()

    if not fecha or not diagnostico:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Fecha y diagnóstico son obligatorios'}), 400
        flash('Fecha y diagnóstico son obligatorios', 'danger')
        return redirect(url_for('historial_medico', id=residente_id))

    cursor = db.database.cursor()
    try:
        # 1. Insertar en historial_medico
        cursor.execute("""
            INSERT INTO historial_medico (residente_id, fecha, diagnostico, observaciones)
            VALUES (%s, %s, %s, %s)
        """, (residente_id, fecha, diagnostico.upper(), observaciones.upper()))
        nuevo_id = cursor.lastrowid
        
        # 2. Obtener nombre del residente (para contexto, aunque no se usa en descripción)
        cursor.execute("""
            SELECT CONCAT(nombre, ' ', apellido1) as nombre_completo
            FROM residentes 
            WHERE id = %s
        """, (residente_id,))
        residente = cursor.fetchone()
        nombre_residente = residente[0] if residente else f"ID {residente_id}"
        
        # 3. Crear registro automático en bitácora (ASUMIMOS que la tabla EXISTE)
        descripcion_bitacora = f"""
Historial Medico
Fecha: {fecha}
Diagnóstico: {diagnostico.upper()}
Observaciones: {observaciones.upper() if observaciones else 'Sin observaciones'}
Registrado por: {current_user.nombre}
""".strip()
        
        cursor.execute("""
            INSERT INTO bitacora_pacientes 
            (residente_id, tipo, descripcion, personal_id, fecha_hora)
            VALUES (%s, 'salud', %s, %s, NOW())
        """, (residente_id, descripcion_bitacora, current_user.id))
        
        db.database.commit()
            
    except Exception as e:
        db.database.rollback()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': f'Error al guardar: {str(e)}'}), 500
        flash(f'Error al guardar registro: {str(e)}', 'danger')
        return redirect(url_for('historial_medico', id=residente_id))
    finally:
        cursor.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'id': nuevo_id,
            'fecha': fecha,
            'fecha_formateada': datetime.strptime(fecha, '%Y-%m-%d').strftime('%d/%m/%Y'),
            'diagnostico': diagnostico.upper(),
            'observaciones': observaciones.upper()
        })

    flash('Registro médico agregado exitosamente', 'success')
    return redirect(url_for('historial_medico', id=residente_id))





@app.route('/historial_medico/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_historial(id):
    cursor = db.database.cursor()
    try:
        cursor.execute("DELETE FROM historial_medico WHERE id = %s", (id,))
        db.database.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()



# Listar usuarios
@app.route('/admin/usuarios')
def admin_usuarios():
    cursor = db.database.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    return render_template('modulos/usuarios/admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/crear', methods=['POST'])
def crear_usuario():
    f = request.form
    
    # 1. VALIDACIÓN BÁSICA (recomendado)
    if not all(k in f for k in ['username', 'correo', 'password', 'nombre', 'rol']):
        flash("Faltan campos requeridos")
        return redirect(url_for('admin_usuarios'))
    
    if len(f['password']) < 8:
        flash("La contraseña debe tener al menos 8 caracteres")
        return redirect(url_for('admin_usuarios'))
    
    # 2. HASH DE LA CONTRASEÑA
    # generate_password_hash usa pbkdf2:sha256 por defecto con salt automático
    password_hash = generate_password_hash(
        f['password'],
        method='pbkdf2:sha256',  # Método por defecto
        salt_length=16           # Longitud del salt (16 es bueno)
    )
    
    # 3. INSERCIÓN EN LA BD
    cursor = db.database.cursor()
    
    # Verificar si el usuario ya existe
    cursor.execute("SELECT id FROM usuarios WHERE username = %s OR correo = %s", 
                   (f['username'], f['correo']))
    if cursor.fetchone():
        cursor.close()
        flash("El usuario o correo ya existe")
        return redirect(url_for('admin_usuarios'))
    
    sql = """
        INSERT INTO usuarios (username, correo, password, nombre, rol, activo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    valores = (
        f['username'], 
        f['correo'], 
        password_hash,  # ← Hash en lugar de texto plano
        f['nombre'],
        f['rol'], 
        1 if 'activo' in f else 0
    )
    
    try:
        cursor.execute(sql, valores)
        db.database.commit()
        flash("Usuario creado exitosamente")
    except Exception as e:
        db.database.rollback()
        flash(f"Error al crear usuario: {str(e)}")
    finally:
        cursor.close()
    
    return redirect(url_for('admin_usuarios'))

from werkzeug.security import generate_password_hash

@app.route('/admin/usuarios/editar/<int:id>', methods=['POST'])
@login_required
def editar_usuario(id):
    f = request.form

    username = f.get('username')
    correo = f.get('correo')
    nombre = f.get('nombre')
    rol = f.get('rol')
    activo = 1 if f.get('activo') else 0
    password = f.get('password')

    cursor = db.database.cursor()

    try:
        # Si se ingresó nueva contraseña
        if password:
            password_hash = generate_password_hash(password)

            sql = """
                UPDATE usuarios
                SET username=%s,
                    correo=%s,
                    password=%s,
                    nombre=%s,
                    rol=%s,
                    activo=%s
                WHERE id=%s
            """
            valores = (username, correo, password_hash, nombre, rol, activo, id)
        else:
            # No modificar password
            sql = """
                UPDATE usuarios
                SET username=%s,
                    correo=%s,
                    nombre=%s,
                    rol=%s,
                    activo=%s
                WHERE id=%s
            """
            valores = (username, correo, nombre, rol, activo, id)

        cursor.execute(sql, valores)
        db.database.commit()
        flash("Usuario actualizado correctamente", "success")

    except Exception as e:
        db.database.rollback()
        flash("Error al actualizar usuario", "danger")
        print("ERROR editar_usuario:", e)

    finally:
        cursor.close()

    return redirect(url_for('admin_usuarios'))


@app.route('/admin/usuarios/eliminar/<int:id>', methods=['POST'])
def eliminar_usuario(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    db.database.commit()
    cursor.close()
    flash("Usuario eliminado")
    return redirect(url_for('admin_usuarios'))


@app.route('/roles')
@login_required
def roles():
    if current_user.rol != 'administrador':
        flash("Acceso restringido a administradores", "danger")
        return redirect(url_for('index_admin'))

    return render_template('roles.html')




# ============================================
# MÓDULO DE CAMAS
# ============================================

@app.route('/camas')
@login_required
@role_required('administrador', 'enfermeria', 'medico', 'asistente_administrativo') 
def listar_camas():
    """Lista todas las camas del centro"""
    # Inicializar variables con valores por defecto
    camas = []
    stats = {}
    zonas = []
    tipos = []
    filtro_estado = request.args.get('estado', '')
    filtro_zona = request.args.get('zona', '')
    filtro_tipo = request.args.get('tipo', '')
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener estadísticas
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) as disponibles,
                SUM(CASE WHEN estado = 'Ocupada' THEN 1 ELSE 0 END) as ocupadas,
                SUM(CASE WHEN estado = 'Mantenimiento' THEN 1 ELSE 0 END) as mantenimiento,
                SUM(CASE WHEN estado = 'Reservada' THEN 1 ELSE 0 END) as reservadas
            FROM camas 
            WHERE activo = TRUE
        """)
        stats = cursor.fetchone() or {}
        
        # ✅ CONSULTA CORREGIDA - INCLUYE ac.id COMO asignacion_actual_id
        query = """
            SELECT 
                c.*, 
                ac.id AS asignacion_actual_id,  -- ← ESTO ES LO QUE FALTABA
                ac.fecha_asignacion,
                DATEDIFF(CURDATE(), ac.fecha_asignacion) as dias_ocupada,
                CASE 
                    WHEN c.estado = 'Ocupada' THEN CONCAT(r.nombre, ' ', r.apellido1)
                    ELSE NULL 
                END AS residente_actual
            FROM camas c
            LEFT JOIN asignacion_camas ac ON c.id = ac.cama_id AND ac.estado = 'Activa'
            LEFT JOIN residentes r ON ac.residente_id = r.id
            WHERE c.activo = TRUE
        """
        
        params = []
        
        if filtro_estado:
            query += " AND c.estado = %s"
            params.append(filtro_estado)
        
        if filtro_zona:
            query += " AND c.zona = %s"
            params.append(filtro_zona)
        
        if filtro_tipo:
            query += " AND c.tipo = %s"
            params.append(filtro_tipo)
        
        query += " ORDER BY c.piso, c.habitacion, c.numero"
        
        cursor.execute(query, tuple(params))
        camas = cursor.fetchall()
        
        # Obtener zonas y tipos únicos para filtros
        cursor.execute("SELECT DISTINCT zona FROM camas WHERE zona IS NOT NULL ORDER BY zona")
        zonas_result = cursor.fetchall()
        zonas = [z['zona'] for z in zonas_result] if zonas_result else []
        
        cursor.execute("SELECT DISTINCT tipo FROM camas WHERE tipo IS NOT NULL ORDER BY tipo")
        tipos_result = cursor.fetchall()
        tipos = [t['tipo'] for t in tipos_result] if tipos_result else []
        
    except Exception as e:
        print(f"Error listando camas: {e}")
        flash(f"Error al cargar camas: {str(e)}", "danger")
    
    finally:
        cursor.close()
    
    return render_template('modulos/camas/listar_camas.html',
                         camas=camas,
                         stats=stats,
                         zonas=zonas,
                         tipos=tipos,
                         filtro_estado=filtro_estado,
                         filtro_zona=filtro_zona,
                         filtro_tipo=filtro_tipo)

@app.route('/camas/nueva', methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def crear_cama():
    """Crea una nueva cama"""
    if request.method == 'POST':
        numero = request.form.get('numero', '').strip().upper()
        habitacion = request.form.get('habitacion', '').strip()
        piso = request.form.get('piso', '').strip()
        zona = request.form.get('zona', 'A')
        tipo = request.form.get('tipo', 'Individual')
        estado = request.form.get('estado', 'Disponible')
        caracteristicas = request.form.get('caracteristicas', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        
        if not numero:
            flash("El número de cama es obligatorio", "danger")
            return redirect(url_for('crear_cama'))
        
        cursor = db.database.cursor()
        
        try:
            # Verificar si el número de cama ya existe
            cursor.execute("SELECT id FROM camas WHERE numero = %s", (numero,))
            if cursor.fetchone():
                flash(f"Ya existe una cama con el número {numero}", "warning")
                return redirect(url_for('crear_cama'))
            
            # Insertar nueva cama
            cursor.execute("""
                INSERT INTO camas 
                (numero, habitacion, piso, zona, tipo, estado, caracteristicas, observaciones)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (numero, habitacion, piso, zona, tipo, estado, caracteristicas, observaciones))
            
            db.database.commit()
            
            # Crear registro en bitácora
            descripcion_bitacora = f"""
NUEVA CAMA REGISTRADA:
Número: {numero}
Habitación: {habitacion}
Piso: {piso}
Zona: {zona}
Tipo: {tipo}
Estado: {estado}
Registrado por: {current_user.nombre}
            """.strip()
            
            # Buscar residente_id ficticio o usar NULL
            cursor.execute("SELECT id FROM residentes LIMIT 1")
            residente_ficticio = cursor.fetchone()
            residente_id = residente_ficticio[0] if residente_ficticio else None
            
            if residente_id:
                cursor.execute("""
                    INSERT INTO bitacora_pacientes 
                    (residente_id, tipo, descripcion, personal_id, fecha_hora)
                    VALUES (%s, 'actividad', %s, %s, NOW())
                """, (residente_id, descripcion_bitacora, current_user.id))
            
            db.database.commit()
            
            flash(f"Cama {numero} creada exitosamente", "success")
            return redirect(url_for('listar_camas'))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al crear cama: {str(e)}", "danger")
            return redirect(url_for('crear_cama'))
        
        finally:
            cursor.close()
    
    return render_template('modulos/camas/crear_cama.html')

@app.route('/camas/<int:cama_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('administrador')
def editar_cama(cama_id):
    """Edita una cama existente"""
    cursor = db.database.cursor(dictionary=True)
    
    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM camas WHERE id = %s", (cama_id,))
            cama = cursor.fetchone()
            
            if not cama:
                flash("Cama no encontrada", "danger")
                return redirect(url_for('listar_camas'))
            
            return render_template('modulos/camas/editar_cama.html', cama=cama)
            
        except Exception as e:
            flash(f"Error al cargar cama: {str(e)}", "danger")
            return redirect(url_for('listar_camas'))
        
        finally:
            cursor.close()
    
    elif request.method == 'POST':
        try:
            # Obtener datos actuales para bitácora
            cursor.execute("SELECT * FROM camas WHERE id = %s", (cama_id,))
            cama_actual = cursor.fetchone()
            
            # Obtener nuevos datos
            numero = request.form.get('numero', '').strip().upper()
            habitacion = request.form.get('habitacion', '').strip()
            piso = request.form.get('piso', '').strip()
            zona = request.form.get('zona', 'A')
            tipo = request.form.get('tipo', 'Individual')
            estado = request.form.get('estado', 'Disponible')
            caracteristicas = request.form.get('caracteristicas', '').strip()
            observaciones = request.form.get('observaciones', '').strip()
            activo = 1 if request.form.get('activo') == 'on' else 0
            
            # Actualizar cama
            cursor.execute("""
                UPDATE camas SET
                    numero = %s,
                    habitacion = %s,
                    piso = %s,
                    zona = %s,
                    tipo = %s,
                    estado = %s,
                    caracteristicas = %s,
                    observaciones = %s,
                    activo = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (numero, habitacion, piso, zona, tipo, estado, caracteristicas, observaciones, activo, cama_id))
            
            # Crear registro en bitácora
            descripcion_bitacora = f"""
CAMA ACTUALIZADA:
Número: {cama_actual['numero']} → {numero}
Habitación: {cama_actual['habitacion']} → {habitacion}
Piso: {cama_actual['piso']} → {piso}
Zona: {cama_actual['zona']} → {zona}
Tipo: {cama_actual['tipo']} → {tipo}
Estado: {cama_actual['estado']} → {estado}
Activo: {'Sí' if cama_actual['activo'] else 'No'} → {'Sí' if activo else 'No'}
Actualizado por: {current_user.nombre}
            """.strip()
            
            # Buscar residente_id para bitácora
            cursor.execute("SELECT residente_id FROM asignacion_camas WHERE cama_id = %s AND estado = 'Activa'", (cama_id,))
            asignacion = cursor.fetchone()
            
            if asignacion:
                cursor.execute("""
                    INSERT INTO bitacora_pacientes 
                    (residente_id, tipo, descripcion, personal_id, fecha_hora)
                    VALUES (%s, 'actividad', %s, %s, NOW())
                """, (asignacion['residente_id'], descripcion_bitacora, current_user.id))
            
            db.database.commit()
            
            flash(f"Cama {numero} actualizada exitosamente", "success")
            return redirect(url_for('listar_camas'))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al actualizar cama: {str(e)}", "danger")
            return redirect(url_for('editar_cama', cama_id=cama_id))
        
        finally:
            cursor.close()

@app.route('/camas/<int:cama_id>/cambiar-estado', methods=['POST'])
@login_required
@role_required('administrador', 'enfermeria', 'asiste_administrativo')
def cambiar_estado_cama(cama_id):
    """Cambia el estado de una cama"""
    nuevo_estado = request.form.get('estado')
    motivo = request.form.get('motivo', '').strip()
    
    if not nuevo_estado:
        return jsonify({'success': False, 'error': 'Estado no proporcionado'}), 400
    
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener datos actuales
        cursor.execute("SELECT * FROM camas WHERE id = %s", (cama_id,))
        cama = cursor.fetchone()
        
        if not cama:
            return jsonify({'success': False, 'error': 'Cama no encontrada'}), 404
        
        # Verificar que no se cambie a Disponible si está ocupada
        if cama['estado'] == 'Ocupada' and nuevo_estado == 'Disponible':
            return jsonify({'success': False, 'error': 'No se puede liberar cama ocupada. Primero libere al residente.'}), 400
        
        # Actualizar estado
        cursor.execute("UPDATE camas SET estado = %s, updated_at = NOW() WHERE id = %s", 
                      (nuevo_estado, cama_id))
        
        # Registrar en bitácora
        descripcion_bitacora = f"""
CAMBIO DE ESTADO DE CAMA:
Cama: {cama['numero']}
Estado anterior: {cama['estado']}
Estado nuevo: {nuevo_estado}
Motivo: {motivo}
Cambiado por: {current_user.nombre}
        """.strip()
        
        # Buscar residente asignado
        cursor.execute("SELECT residente_id FROM asignacion_camas WHERE cama_id = %s AND estado = 'Activa'", (cama_id,))
        asignacion = cursor.fetchone()
        
        if asignacion:
            cursor.execute("""
                INSERT INTO bitacora_pacientes 
                (residente_id, tipo, descripcion, personal_id, fecha_hora)
                VALUES (%s, 'incidente', %s, %s, NOW())
            """, (asignacion['residente_id'], descripcion_bitacora, current_user.id))
        
        db.database.commit()
        
        return jsonify({'success': True, 'estado': nuevo_estado})
        
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        cursor.close()

@app.route('/camas/asignar/<int:residente_id>', methods=['GET', 'POST'])
@login_required
@role_required('enfermeria', 'medico', 'administrador', 'asistente_administrativo')
def asignar_cama(residente_id):
    """Asigna una cama a un residente"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Verificar que el residente existe
        cursor.execute("SELECT * FROM residentes WHERE id = %s", (residente_id,))
        residente = cursor.fetchone()
        
        if not residente:
            flash("Residente no encontrado", "danger")
            return redirect(request.referrer or url_for('listar_residentes'))
        
        # Verificar si ya tiene cama asignada
        cursor.execute("""
            SELECT ac.*, c.numero, c.habitacion 
            FROM asignacion_camas ac
            JOIN camas c ON ac.cama_id = c.id
            WHERE ac.residente_id = %s AND ac.estado = 'Activa'
        """, (residente_id,))
        
        cama_actual = cursor.fetchone()
        
        if request.method == 'POST':
            cama_id = request.form.get('cama_id')
            motivo = request.form.get('motivo', 'Ingreso')
            observaciones = request.form.get('observaciones', '').strip()
            
            if not cama_id:
                flash("Debe seleccionar una cama", "danger")
                return redirect(url_for('asignar_cama', residente_id=residente_id))
            
            # Verificar que la cama esté disponible
            cursor.execute("SELECT * FROM camas WHERE id = %s AND activo = TRUE", (cama_id,))
            cama = cursor.fetchone()
            
            if not cama:
                flash("Cama no disponible", "danger")
                return redirect(url_for('asignar_cama', residente_id=residente_id))
            
            if cama['estado'] != 'Disponible':
                flash(f"La cama {cama['numero']} no está disponible. Estado: {cama['estado']}", "warning")
                return redirect(url_for('asignar_cama', residente_id=residente_id))
            
            # Si ya tiene cama, finalizar asignación anterior
            if cama_actual:
                cursor.execute("""
                    UPDATE asignacion_camas 
                    SET estado = 'Finalizada', fecha_liberacion = CURDATE()
                    WHERE id = %s
                """, (cama_actual['id'],))
                
                # Registrar en historial de cambios
                cursor.execute("""
                    INSERT INTO historial_cambios_cama 
                    (residente_id, cama_anterior_id, cama_nueva_id, motivo, cambiado_por)
                    VALUES (%s, %s, %s, %s, %s)
                """, (residente_id, cama_actual['cama_id'], cama_id, 'Transferencia', current_user.id))
            
            # Crear nueva asignación
            cursor.execute("""
                INSERT INTO asignacion_camas 
                (cama_id, residente_id, fecha_asignacion, motivo, observaciones, asignado_por)
                VALUES (%s, %s, CURDATE(), %s, %s, %s)
            """, (cama_id, residente_id, motivo, observaciones, current_user.id))
            
            # Actualizar estado de la cama
            cursor.execute("UPDATE camas SET estado = 'Ocupada', updated_at = NOW() WHERE id = %s", (cama_id,))
            
            # Bitácora
            descripcion_bitacora = f"""
ASIGNACIÓN DE CAMA:
Cama asignada: {cama['numero']} (Habitación: {cama['habitacion']})
Motivo: {motivo}
Observaciones: {observaciones}

            """.strip()
            
            cursor.execute("""
                INSERT INTO bitacora_pacientes 
                (residente_id, tipo, descripcion, personal_id, fecha_hora)
                VALUES (%s, 'actividad', %s, %s, NOW())
            """, (residente_id, descripcion_bitacora, current_user.id))
            
            db.database.commit()
            
            flash(f"Cama {cama['numero']} asignada exitosamente a {residente['nombre']}", "success")
            return redirect(url_for('index_ver_info', id=residente_id))  # ← CORREGIDO: 'index_ver_info'
        
        # GET: Mostrar camas disponibles
        # Filtros
        zona_preferida = request.args.get('zona', '')
        tipo_preferido = request.args.get('tipo', '')
        
        query = """
            SELECT c.*
            FROM camas c
            WHERE c.activo = TRUE 
            AND c.estado = 'Disponible'
        """
        
        params = []
        
        if zona_preferida:
            query += " AND c.zona = %s"
            params.append(zona_preferida)
        
        if tipo_preferido:
            query += " AND c.tipo = %s"
            params.append(tipo_preferido)
        
        query += " ORDER BY c.piso, c.habitacion, c.numero"
        
        cursor.execute(query, tuple(params))
        camas_disponibles = cursor.fetchall()
        
        # Obtener zonas y tipos para filtros
        cursor.execute("SELECT DISTINCT zona FROM camas WHERE activo = TRUE ORDER BY zona")
        zonas = [z['zona'] for z in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT tipo FROM camas WHERE activo = TRUE ORDER BY tipo")
        tipos = [t['tipo'] for t in cursor.fetchall()]
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al procesar asignación: {str(e)}", "danger")
        return redirect(request.referrer or url_for('ver_info', id=residente_id))
    
    finally:
        cursor.close()
    
    return render_template('modulos/camas/asignar_cama.html',
                         residente=residente,
                         cama_actual=cama_actual,
                         camas_disponibles=camas_disponibles,
                         zonas=zonas,
                         tipos=tipos,
                         zona_preferida=zona_preferida,
                         tipo_preferido=tipo_preferido)

@app.route('/camas/liberar/<int:asignacion_id>', methods=['POST'])
@login_required
@role_required('enfermeria', 'medico', 'administrador', 'asistente_administrativo')
def liberar_cama(asignacion_id):
    """Libera una cama ocupada"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener información de la asignación
        cursor.execute("""
            SELECT ac.*, c.id as cama_id, c.numero
            FROM asignacion_camas ac
            JOIN camas c ON ac.cama_id = c.id
            WHERE ac.id = %s AND ac.estado = 'Activa'
        """, (asignacion_id,))
        
        asignacion = cursor.fetchone()
        
        if not asignacion:
            return jsonify({'success': False, 'error': 'Asignación no encontrada'}), 404
        
        motivo = request.form.get('motivo_liberacion', 'Ingreso')
        
        # SOLO ACTUALIZAR LO NECESARIO - SIN COLUMNA TIPO
        cursor.execute("""
            UPDATE asignacion_camas 
            SET estado = 'Finalizada', 
                fecha_liberacion = CURDATE()
            WHERE id = %s
        """, (asignacion_id,))
        
        # Actualizar estado de la cama
        cursor.execute("""
            UPDATE camas 
            SET estado = 'Disponible', 
                updated_at = NOW() 
            WHERE id = %s
        """, (asignacion['cama_id'],))
        
        db.database.commit()
        
        return jsonify({
            'success': True,
            'message': f'Cama {asignacion["numero"]} liberada'
        })
        
    except Exception as e:
        db.database.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        cursor.close()

@app.route('/camas/dashboard')
@login_required
@role_required('administrador', 'enfermeria', 'medico', 'asistente_administrativo')
def dashboard_camas():
    """Dashboard con estadísticas detalladas de camas"""
    cursor = db.database.cursor(dictionary=True)
    
    # Inicializar todas las variables con valores por defecto
    stats_zona = []
    stats_tiempo = []
    camas_mantenimiento = []
    proximas_liberaciones = []
    
    try:
        # Estadísticas por zona
        cursor.execute("""
            SELECT 
                zona,
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) as disponibles,
                SUM(CASE WHEN estado = 'Ocupada' THEN 1 ELSE 0 END) as ocupadas,
                SUM(CASE WHEN estado = 'Mantenimiento' THEN 1 ELSE 0 END) as mantenimiento,
                ROUND(SUM(CASE WHEN estado = 'Ocupada' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as porcentaje_ocupacion
            FROM camas 
            WHERE activo = TRUE
            GROUP BY zona
            ORDER BY zona
        """)
        stats_zona = cursor.fetchall()
        
        # Ocupación por día de la semana (si hay datos)
        try:
            cursor.execute("""
                SELECT 
                    DAYNAME(fecha_asignacion) as dia_semana,
                    COUNT(*) as ingresos,
                    AVG(DATEDIFF(COALESCE(fecha_liberacion, CURDATE()), fecha_asignacion)) as promedio_dias
                FROM asignacion_camas
                WHERE fecha_asignacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DAYNAME(fecha_asignacion), DAYOFWEEK(fecha_asignacion)
                ORDER BY DAYOFWEEK(fecha_asignacion)
            """)
            stats_tiempo = cursor.fetchall()
        except Exception as e:
            print(f"Error en stats_tiempo: {e}")
            stats_tiempo = []
        
        # Camas que requieren mantenimiento
        try:
            cursor.execute("""
                SELECT c.*, 
                       DATEDIFF(CURDATE(), a.fecha_asignacion) as dias_ocupada_actual,
                       r.nombre, r.apellido1
                FROM camas c
                LEFT JOIN asignacion_camas a ON c.id = a.cama_id AND a.estado = 'Activa'
                LEFT JOIN residentes r ON a.residente_id = r.id
                WHERE c.estado = 'Mantenimiento'
                AND c.activo = TRUE
                ORDER BY c.updated_at DESC
                LIMIT 10
            """)
            camas_mantenimiento = cursor.fetchall()
        except Exception as e:
            print(f"Error en camas_mantenimiento: {e}")
            camas_mantenimiento = []
        
        # Próximas liberaciones (en los próximos 3 días)
        try:
            cursor.execute("""
                SELECT 
                    c.numero, c.habitacion, c.zona,
                    r.nombre, r.apellido1,
                    a.fecha_asignacion,
                    DATE_ADD(a.fecha_asignacion, INTERVAL 14 DAY) as posible_alta,
                    DATEDIFF(DATE_ADD(a.fecha_asignacion, INTERVAL 14 DAY), CURDATE()) as dias_restantes
                FROM asignacion_camas a
                JOIN camas c ON a.cama_id = c.id
                JOIN residentes r ON a.residente_id = r.id
                WHERE a.estado = 'Activa'
                AND a.fecha_asignacion <= DATE_SUB(CURDATE(), INTERVAL 11 DAY) -- Más de 11 días ocupada
                ORDER BY posible_alta ASC
                LIMIT 10
            """)
            proximas_liberaciones = cursor.fetchall()
        except Exception as e:
            print(f"Error en proximas_liberaciones: {e}")
            proximas_liberaciones = []
        
    except Exception as e:
        print(f"Error en dashboard: {e}")
        flash(f"Error al cargar dashboard: {str(e)}", "danger")
    
    finally:
        cursor.close()
    
    # Calcular estadísticas generales
    total_camas = 0
    disponibles = 0
    ocupadas = 0
    mantenimiento = 0
    
    for zona in stats_zona:
        total_camas += zona.get('total', 0) or 0
        disponibles += zona.get('disponibles', 0) or 0
        ocupadas += zona.get('ocupadas', 0) or 0
        mantenimiento += zona.get('mantenimiento', 0) or 0
    
    stats = {
        'total': total_camas,
        'disponibles': disponibles,
        'ocupadas': ocupadas,
        'mantenimiento': mantenimiento
    }
    
    return render_template('modulos/camas/dashboard_camas.html',
                         stats=stats,
                         stats_zona=stats_zona,
                         stats_tiempo=stats_tiempo,
                         camas_mantenimiento=camas_mantenimiento,
                         proximas_liberaciones=proximas_liberaciones)
# ============================================
# FUNCIÓN PRINCIPAL ACTUALIZADA PARA PASAR ESTADÍSTICAS
# ============================================

@app.route('/camas/asignar/seleccionar-residente')
@login_required
@role_required('administrador', 'enfermeria', 'medico', 'asistente_administrativo')
def seleccionar_residente_asignacion():
    """Lista residentes sin cama para asignación"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener residentes activos sin cama asignada
        cursor.execute("""
            SELECT r.*, 
                   CONCAT(r.nombre, ' ', r.apellido1, ' ', COALESCE(r.apellido2, '')) as nombre_completo,
                   TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) as edad
            FROM residentes r
            WHERE r.activo = 1
              AND r.id NOT IN (
                  SELECT residente_id 
                  FROM asignacion_camas 
                  WHERE estado = 'Activa'
              )
            ORDER BY r.nombre, r.apellido1
        """)
        residentes_sin_cama = cursor.fetchall()
        
        # También mostrar residentes con cama (para transferencias)
        cursor.execute("""
            SELECT r.*, 
                   CONCAT(r.nombre, ' ', r.apellido1, ' ', COALESCE(r.apellido2, '')) as nombre_completo,
                   ac.cama_id,
                   c.numero as cama_actual,
                   TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) as edad
            FROM residentes r
            JOIN asignacion_camas ac ON r.id = ac.residente_id AND ac.estado = 'Activa'
            JOIN camas c ON ac.cama_id = c.id
            WHERE r.activo = 1
            ORDER BY r.nombre, r.apellido1
        """)
        residentes_con_cama = cursor.fetchall()
        
    except Exception as e:
        print(f"Error listando residentes: {e}")
        residentes_sin_cama = []
        residentes_con_cama = []
        flash(f"Error al cargar residentes: {str(e)}", "danger")
    
    finally:
        cursor.close()
    
    return render_template('modulos/camas/seleccionar_residente.html',
                         residentes_sin_cama=residentes_sin_cama,
                         residentes_con_cama=residentes_con_cama)


@app.route('/index_admin')
@login_required
def index_admin():
    """Página principal con menú de módulos"""
    
    # Obtener estadísticas de camas si el usuario tiene acceso
    cama_stats = None
    if current_user.rol in ['administrador', 'enfermeria', 'medico']:
        cursor = db.database.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) as disponibles,
                    SUM(CASE WHEN estado = 'Ocupada' THEN 1 ELSE 0 END) as ocupadas,
                    SUM(CASE WHEN estado = 'Mantenimiento' THEN 1 ELSE 0 END) as mantenimiento
                FROM camas 
                WHERE activo = TRUE
            """)
            cama_stats = cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo estadísticas de camas: {e}")
            cama_stats = {
                'total': 0,
                'disponibles': 0,
                'ocupadas': 0,
                'mantenimiento': 0
            }
        finally:
            cursor.close()
    
    # Solo mostrar modal si es la primera vez
    mostrar_modal = session.get('mostrar_modal', True)
    
    return render_template('index.html', 
                         usuario=current_user.username, 
                         rol=current_user.rol,
                         cama_stats=cama_stats,
                         mostrar_modal=mostrar_modal)

# ============================================
# FUNCIONES AUXILIARES PARA TEMPLATES
# ============================================

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    """Filtro para formatear fechas en templates"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except:
                return value
    return value.strftime(format)

@app.template_filter('dateformat')
def dateformat(value, format='%d/%m/%Y'):
    """Filtro para formatear solo fechas en templates"""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            return value
    return value.strftime(format)









# ============================================
# MÓDULO DE INVENTARIOS - TESINA
# ============================================

# ------------------------------------------------------------
# LISTAR INSUMOS
# ------------------------------------------------------------
@app.route('/inventario/insumos')
@login_required
@role_required('bodega', 'farmacia', 'administrador', 'asistente_administrativo')
def listar_insumos():
    """Lista todos los insumos del inventario"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Filtros básicos
        categoria_id = request.args.get('categoria', '')
        busqueda = request.args.get('q', '')
        
        query = """
            SELECT i.*, c.nombre as categoria_nombre, p.nombre as proveedor_nombre
            FROM insumos i
            LEFT JOIN categorias_insumos c ON i.categoria_id = c.id
            LEFT JOIN proveedores p ON i.proveedor_id = p.id
            WHERE i.activo = TRUE
        """
        params = []
        
        if categoria_id:
            query += " AND i.categoria_id = %s"
            params.append(categoria_id)
        
        if busqueda:
            query += " AND (i.nombre LIKE %s OR i.codigo LIKE %s)"
            params.extend([f"%{busqueda}%", f"%{busqueda}%"])
        
        query += " ORDER BY i.nombre"
        
        cursor.execute(query, params)
        insumos = cursor.fetchall()
        
        # Categorías para filtro
        cursor.execute("SELECT * FROM categorias_insumos WHERE activo = TRUE ORDER BY nombre")
        categorias = cursor.fetchall()
        
    except Exception as e:
        print(f"Error listando insumos: {e}")
        insumos = []
        categorias = []
        flash(f"Error al cargar insumos: {str(e)}", "danger")
    
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/insumos.html',
                         insumos=insumos,
                         categorias=categorias,
                         filtro_categoria=categoria_id,
                         busqueda=busqueda)


# ------------------------------------------------------------
# NUEVO INSUMO
# ------------------------------------------------------------
@app.route('/inventario/insumos/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('bodega', 'farmacia', 'administrador', 'asistente_administrativo')
def nuevo_insumo():
    """Crea un nuevo insumo"""
    cursor = db.database.cursor(dictionary=True)
    
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip().upper()
        nombre = request.form.get('nombre', '').strip().upper()
        descripcion = request.form.get('descripcion', '').strip()
        categoria_id = request.form.get('categoria_id')
        proveedor_id = request.form.get('proveedor_id')
        unidad_medida = request.form.get('unidad_medida', '').strip()
        stock_actual = request.form.get('stock_actual', 0)
        stock_minimo = request.form.get('stock_minimo', 5)
        precio_compra = request.form.get('precio_compra') or None
        
        if not codigo or not nombre:
            flash("Código y nombre son obligatorios", "danger")
            return redirect(url_for('nuevo_insumo'))
        
        try:
            # Verificar si el código ya existe
            cursor.execute("SELECT id FROM insumos WHERE codigo = %s", (codigo,))
            if cursor.fetchone():
                flash(f"Ya existe un insumo con código {codigo}", "warning")
                return redirect(url_for('nuevo_insumo'))
            
            # Insertar insumo
            cursor.execute("""
                INSERT INTO insumos 
                (codigo, nombre, descripcion, categoria_id, proveedor_id, 
                 unidad_medida, stock_actual, stock_minimo, precio_compra)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (codigo, nombre, descripcion, categoria_id, proveedor_id,
                 unidad_medida, stock_actual, stock_minimo, precio_compra))
            
            insumo_id = cursor.lastrowid
            
            # Registrar movimiento inicial si hay stock
            if int(stock_actual) > 0:
                cursor.execute("""
                    INSERT INTO movimientos_inventario 
                    (insumo_id, tipo, cantidad, stock_anterior, stock_nuevo, usuario_id, observacion)
                    VALUES (%s, 'Entrada', %s, 0, %s, %s, 'Stock inicial')
                """, (insumo_id, stock_actual, stock_actual, current_user.id))
            
            db.database.commit()
            flash(f"Insumo {codigo} creado exitosamente", "success")
            return redirect(url_for('listar_insumos'))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al crear insumo: {str(e)}", "danger")
    
    # GET: cargar datos para formulario
    try:
        cursor.execute("SELECT * FROM categorias_insumos WHERE activo = TRUE ORDER BY nombre")
        categorias = cursor.fetchall()
        
        cursor.execute("SELECT * FROM proveedores WHERE activo = TRUE ORDER BY nombre")
        proveedores = cursor.fetchall()
    except Exception as e:
        categorias = []
        proveedores = []
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/nuevo_insumo.html',
                         categorias=categorias,
                         proveedores=proveedores)


# ------------------------------------------------------------
# EDITAR INSUMO
# ------------------------------------------------------------
@app.route('/inventario/insumos/<int:insumo_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('bodega', 'farmacia', 'administrador')
def editar_insumo(insumo_id):
    """Edita un insumo existente"""
    cursor = db.database.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo', '').strip().upper()
            nombre = request.form.get('nombre', '').strip().upper()
            descripcion = request.form.get('descripcion', '').strip()
            categoria_id = request.form.get('categoria_id')
            proveedor_id = request.form.get('proveedor_id')
            unidad_medida = request.form.get('unidad_medida', '').strip()
            stock_minimo = request.form.get('stock_minimo', 5)
            precio_compra = request.form.get('precio_compra') or None
            activo = 1 if request.form.get('activo') else 0
            
            # Verificar código duplicado
            cursor.execute("SELECT id FROM insumos WHERE codigo = %s AND id != %s", (codigo, insumo_id))
            if cursor.fetchone():
                flash(f"Ya existe otro insumo con código {codigo}", "warning")
                return redirect(url_for('editar_insumo', insumo_id=insumo_id))
            
            # Actualizar insumo
            cursor.execute("""
                UPDATE insumos SET
                    codigo = %s,
                    nombre = %s,
                    descripcion = %s,
                    categoria_id = %s,
                    proveedor_id = %s,
                    unidad_medida = %s,
                    stock_minimo = %s,
                    precio_compra = %s,
                    activo = %s,
                    created_at = created_at
                WHERE id = %s
            """, (codigo, nombre, descripcion, categoria_id, proveedor_id,
                 unidad_medida, stock_minimo, precio_compra, activo, insumo_id))
            
            db.database.commit()
            flash(f"Insumo {codigo} actualizado exitosamente", "success")
            return redirect(url_for('listar_insumos'))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al actualizar insumo: {str(e)}", "danger")
    
    # GET: cargar datos del insumo
    try:
        cursor.execute("SELECT * FROM insumos WHERE id = %s", (insumo_id,))
        insumo = cursor.fetchone()
        
        if not insumo:
            flash("Insumo no encontrado", "danger")
            return redirect(url_for('listar_insumos'))
        
        cursor.execute("SELECT * FROM categorias_insumos WHERE activo = TRUE ORDER BY nombre")
        categorias = cursor.fetchall()
        
        cursor.execute("SELECT * FROM proveedores WHERE activo = TRUE ORDER BY nombre")
        proveedores = cursor.fetchall()
        
    except Exception as e:
        flash(f"Error al cargar datos: {str(e)}", "danger")
        return redirect(url_for('listar_insumos'))
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/editar_insumo.html',
                         insumo=insumo,
                         categorias=categorias,
                         proveedores=proveedores)


# ------------------------------------------------------------
# AJUSTAR STOCK
# ------------------------------------------------------------
@app.route('/inventario/insumos/<int:insumo_id>/ajustar-stock', methods=['POST'])
@login_required
@role_required('bodega', 'farmacia', 'administrador')
def ajustar_stock(insumo_id):
    """Realiza un ajuste de stock manual"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        cantidad = int(request.form.get('cantidad', 0))
        tipo = request.form.get('tipo', 'Ajuste')
        observacion = request.form.get('observacion', '').strip()
        
        if cantidad == 0:
            flash("La cantidad debe ser diferente de cero", "danger")
            return redirect(url_for('listar_insumos'))
        
        # Obtener stock actual
        cursor.execute("SELECT stock_actual, nombre FROM insumos WHERE id = %s", (insumo_id,))
        insumo = cursor.fetchone()
        
        if not insumo:
            flash("Insumo no encontrado", "danger")
            return redirect(url_for('listar_insumos'))
        
        stock_anterior = insumo['stock_actual']
        stock_nuevo = stock_anterior + cantidad
        
        if stock_nuevo < 0:
            flash("El stock no puede ser negativo", "danger")
            return redirect(url_for('listar_insumos'))
        
        # Actualizar stock
        cursor.execute("UPDATE insumos SET stock_actual = %s WHERE id = %s", (stock_nuevo, insumo_id))
        
        # Registrar movimiento
        cursor.execute("""
            INSERT INTO movimientos_inventario 
            (insumo_id, tipo, cantidad, stock_anterior, stock_nuevo, usuario_id, observacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (insumo_id, tipo, cantidad, stock_anterior, stock_nuevo, current_user.id, observacion))
        
        db.database.commit()
        flash(f"Stock ajustado correctamente. Nuevo stock: {stock_nuevo}", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al ajustar stock: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('listar_insumos'))


# ------------------------------------------------------------
# ELIMINAR INSUMO (DESACTIVAR)
# ------------------------------------------------------------
@app.route('/inventario/insumos/<int:insumo_id>/eliminar', methods=['POST'])
@login_required
@role_required('bodega', 'administrador')
def eliminar_insumo(insumo_id):
    cursor = db.database.cursor()
    
    try:
        cursor.execute("UPDATE insumos SET activo = FALSE WHERE id = %s", (insumo_id,))
        db.database.commit()
        flash("Insumo desactivado correctamente", "success")
    except Exception as e:
        db.database.rollback()
        flash(f"Error al desactivar insumo: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('listar_insumos'))


# ------------------------------------------------------------
# LISTAR PROVEEDORES
# ------------------------------------------------------------
@app.route('/inventario/proveedores')
@login_required
@role_required('bodega', 'administrador', 'asistente_administrativo')
def listar_proveedores():
    """Lista todos los proveedores"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT p.*, COUNT(i.id) as total_insumos
            FROM proveedores p
            LEFT JOIN insumos i ON p.id = i.proveedor_id AND i.activo = TRUE
            WHERE p.activo = TRUE
            GROUP BY p.id
            ORDER BY p.nombre
        """)
        proveedores = cursor.fetchall()
        
    except Exception as e:
        print(f"Error listando proveedores: {e}")
        proveedores = []
        flash(f"Error al cargar proveedores: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/proveedores.html',
                         proveedores=proveedores)


# ------------------------------------------------------------
# NUEVO PROVEEDOR
# ------------------------------------------------------------
@app.route('/inventario/proveedores/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('bodega', 'administrador')
def nuevo_proveedor():
    """Crea un nuevo proveedor"""
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip().upper()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip().upper()
        
        if not nombre:
            flash("El nombre del proveedor es obligatorio", "danger")
            return redirect(url_for('nuevo_proveedor'))
        
        cursor = db.database.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO proveedores (nombre, telefono, email, direccion)
                VALUES (%s, %s, %s, %s)
            """, (nombre, telefono, email, direccion))
            
            db.database.commit()
            flash(f"Proveedor {nombre} creado exitosamente", "success")
            return redirect(url_for('listar_proveedores'))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al crear proveedor: {str(e)}", "danger")
        finally:
            cursor.close()
    
    return render_template('modulos/inventarios/nuevo_proveedor.html')


# ------------------------------------------------------------
# EDITAR PROVEEDOR
# ------------------------------------------------------------
@app.route('/inventario/proveedores/<int:proveedor_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('bodega', 'administrador')
def editar_proveedor(proveedor_id):
    """Edita un proveedor existente"""
    cursor = db.database.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre', '').strip().upper()
            telefono = request.form.get('telefono', '').strip()
            email = request.form.get('email', '').strip()
            direccion = request.form.get('direccion', '').strip().upper()
            activo = 1 if request.form.get('activo') else 0
            
            cursor.execute("""
                UPDATE proveedores SET
                    nombre = %s,
                    telefono = %s,
                    email = %s,
                    direccion = %s,
                    activo = %s
                WHERE id = %s
            """, (nombre, telefono, email, direccion, activo, proveedor_id))
            
            db.database.commit()
            flash(f"Proveedor {nombre} actualizado exitosamente", "success")
            return redirect(url_for('listar_proveedores'))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al actualizar proveedor: {str(e)}", "danger")
    
    # GET: cargar datos del proveedor
    try:
        cursor.execute("SELECT * FROM proveedores WHERE id = %s", (proveedor_id,))
        proveedor = cursor.fetchone()
        
        if not proveedor:
            flash("Proveedor no encontrado", "danger")
            return redirect(url_for('listar_proveedores'))
            
    except Exception as e:
        flash(f"Error al cargar datos: {str(e)}", "danger")
        return redirect(url_for('listar_proveedores'))
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/editar_proveedor.html',
                         proveedor=proveedor)


# ------------------------------------------------------------
# ELIMINAR PROVEEDOR (DESACTIVAR)
# ------------------------------------------------------------
@app.route('/inventario/proveedores/<int:proveedor_id>/eliminar', methods=['POST'])
@login_required
@role_required('administrador')
def eliminar_proveedor(proveedor_id):
    """Desactiva un proveedor"""
    cursor = db.database.cursor()
    
    try:
        cursor.execute("UPDATE proveedores SET activo = FALSE WHERE id = %s", (proveedor_id,))
        db.database.commit()
        flash("Proveedor desactivado correctamente", "success")
    except Exception as e:
        db.database.rollback()
        flash(f"Error al desactivar proveedor: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('listar_proveedores'))


# ------------------------------------------------------------
# LISTAR ÓRDENES DE COMPRA
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra')
@login_required
@role_required('bodega', 'administrador', 'asistente_administrativo')
def listar_ordenes_compra():
    """Lista todas las órdenes de compra"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT o.*, p.nombre as proveedor_nombre, u.nombre as creador_nombre
            FROM ordenes_compra o
            JOIN proveedores p ON o.proveedor_id = p.id
            LEFT JOIN usuarios u ON o.creado_por = u.id
            ORDER BY o.fecha DESC, o.id DESC
        """)
        ordenes = cursor.fetchall()
        
    except Exception as e:
        print(f"Error listando órdenes: {e}")
        ordenes = []
        flash(f"Error al cargar órdenes de compra: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/ordenes_compra.html',
                         ordenes=ordenes)


# ------------------------------------------------------------
# NUEVA ORDEN DE COMPRA
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra/nueva', methods=['GET', 'POST'])
@login_required
@role_required('bodega', 'administrador' , 'asistente_administrativo')
def nueva_orden_compra():
    """Crea una nueva orden de compra"""
    cursor = db.database.cursor(dictionary=True)
    
    if request.method == 'POST':
        proveedor_id = request.form.get('proveedor_id')
        fecha = request.form.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        
        if not proveedor_id:
            flash("Debe seleccionar un proveedor", "danger")
            return redirect(url_for('nueva_orden_compra'))
        
        # Generar número de orden automático
        numero_orden = f"OC-{datetime.now().year}-{datetime.now().strftime('%m%d%H%M%S')}"
        
        try:
            cursor.execute("""
                INSERT INTO ordenes_compra 
                (numero_orden, proveedor_id, fecha, creado_por)
                VALUES (%s, %s, %s, %s)
            """, (numero_orden, proveedor_id, fecha, current_user.id))
            
            orden_id = cursor.lastrowid
            db.database.commit()
            
            flash(f"Orden de compra {numero_orden} creada", "success")
            return redirect(url_for('editar_orden_compra', orden_id=orden_id))
            
        except Exception as e:
            db.database.rollback()
            flash(f"Error al crear orden: {str(e)}", "danger")
    
    # GET: cargar proveedores
    try:
        cursor.execute("SELECT * FROM proveedores WHERE activo = TRUE ORDER BY nombre")
        proveedores = cursor.fetchall()
        
        cursor.execute("SELECT * FROM insumos WHERE activo = TRUE ORDER BY nombre")
        insumos = cursor.fetchall()
    except Exception as e:
        proveedores = []
        insumos = []
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/nueva_orden_compra.html',
                         proveedores=proveedores,
                         insumos=insumos,
                         hoy=datetime.now().strftime('%Y-%m-%d'))


# ------------------------------------------------------------
# VER/EDITAR ORDEN DE COMPRA
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra/<int:orden_id>')
@login_required
@role_required('bodega', 'administrador')
def editar_orden_compra(orden_id):
    """Ver/editar una orden de compra"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener orden
        cursor.execute("""
            SELECT o.*, p.nombre as proveedor_nombre, u.nombre as creador_nombre
            FROM ordenes_compra o
            JOIN proveedores p ON o.proveedor_id = p.id
            LEFT JOIN usuarios u ON o.creado_por = u.id
            WHERE o.id = %s
        """, (orden_id,))
        orden = cursor.fetchone()
        
        if not orden:
            flash("Orden de compra no encontrada", "danger")
            return redirect(url_for('listar_ordenes_compra'))
        
        # Obtener detalles
        cursor.execute("""
            SELECT od.*, i.nombre, i.codigo, i.unidad_medida
            FROM orden_compra_detalles od
            JOIN insumos i ON od.insumo_id = i.id
            WHERE od.orden_id = %s
        """, (orden_id,))
        detalles = cursor.fetchall()
        
        # Calcular total
        total = sum(d['cantidad'] * d['precio_unitario'] for d in detalles) if detalles else 0
        
        # Actualizar total en orden
        cursor.execute("UPDATE ordenes_compra SET total = %s WHERE id = %s", (total, orden_id))
        db.database.commit()
        
        # Insumos para agregar más
        cursor.execute("SELECT * FROM insumos WHERE activo = TRUE ORDER BY nombre")
        insumos = cursor.fetchall()
        
    except Exception as e:
        flash(f"Error al cargar orden: {str(e)}", "danger")
        return redirect(url_for('listar_ordenes_compra'))
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/editar_orden_compra.html',
                         orden=orden,
                         detalles=detalles,
                         total=total,
                         insumos=insumos)


# ------------------------------------------------------------
# AGREGAR DETALLE A ORDEN
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra/<int:orden_id>/agregar-detalle', methods=['POST'])
@login_required
@role_required('bodega', 'administrador')
def agregar_detalle_orden(orden_id):
    """Agrega un insumo a la orden de compra"""
    insumo_id = request.form.get('insumo_id')
    cantidad = request.form.get('cantidad')
    precio_unitario = request.form.get('precio_unitario')
    
    if not all([insumo_id, cantidad, precio_unitario]):
        flash("Todos los campos son obligatorios", "danger")
        return redirect(url_for('editar_orden_compra', orden_id=orden_id))
    
    cursor = db.database.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO orden_compra_detalles 
            (orden_id, insumo_id, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
        """, (orden_id, insumo_id, cantidad, precio_unitario))
        
        db.database.commit()
        flash("Insumo agregado a la orden", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al agregar insumo: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('editar_orden_compra', orden_id=orden_id))


# ------------------------------------------------------------
# ELIMINAR DETALLE DE ORDEN
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra/eliminar-detalle/<int:detalle_id>', methods=['POST'])
@login_required
@role_required('administrador')
def eliminar_detalle_orden(detalle_id):
    """Elimina un detalle de la orden de compra"""
    cursor = db.database.cursor()
    
    try:
        cursor.execute("SELECT orden_id FROM orden_compra_detalles WHERE id = %s", (detalle_id,))
        detalle = cursor.fetchone()
        
        if not detalle:
            flash("Detalle no encontrado", "danger")
            return redirect(url_for('listar_ordenes_compra'))
        
        orden_id = detalle[0]
        
        cursor.execute("DELETE FROM orden_compra_detalles WHERE id = %s", (detalle_id,))
        db.database.commit()
        
        flash("Insumo eliminado de la orden", "success")
        return redirect(url_for('editar_orden_compra', orden_id=orden_id))
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al eliminar detalle: {str(e)}", "danger")
        return redirect(url_for('listar_ordenes_compra'))
    finally:
        cursor.close()


# ------------------------------------------------------------
# CAMBIAR ESTADO DE LA ORDEN
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra/<int:orden_id>/cambiar-estado', methods=['POST'])
@login_required
@role_required('bodega', 'administrador')
def cambiar_estado_orden(orden_id):
    """Cambia el estado de una orden de compra"""
    nuevo_estado = request.form.get('estado')
    
    if not nuevo_estado:
        flash("Estado no proporcionado", "danger")
        return redirect(url_for('listar_ordenes_compra'))
    
    cursor = db.database.cursor()
    
    try:
        cursor.execute("UPDATE ordenes_compra SET estado = %s WHERE id = %s", (nuevo_estado, orden_id))
        db.database.commit()
        flash(f"Estado de orden actualizado a {nuevo_estado}", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al cambiar estado: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('listar_ordenes_compra'))


# ------------------------------------------------------------
# RECIBIR ORDEN Y ACTUALIZAR INVENTARIO
# ------------------------------------------------------------
@app.route('/inventario/ordenes-compra/<int:orden_id>/recibir', methods=['POST'])
@login_required
@role_required('bodega', 'administrador' , 'asistente_administrativo')
def recibir_orden_compra(orden_id):
    """Marca orden como recibida y actualiza stock"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Obtener detalles
        cursor.execute("""
            SELECT od.*, i.stock_actual
            FROM orden_compra_detalles od
            JOIN insumos i ON od.insumo_id = i.id
            WHERE od.orden_id = %s
        """, (orden_id,))
        detalles = cursor.fetchall()
        
        for detalle in detalles:
            # Actualizar stock
            nuevo_stock = detalle['stock_actual'] + detalle['cantidad']
            cursor.execute("UPDATE insumos SET stock_actual = %s WHERE id = %s", 
                         (nuevo_stock, detalle['insumo_id']))
            
            # Registrar movimiento
            cursor.execute("""
                INSERT INTO movimientos_inventario 
                (insumo_id, tipo, cantidad, stock_anterior, stock_nuevo, usuario_id, observacion)
                VALUES (%s, 'Entrada', %s, %s, %s, %s, %s)
            """, (detalle['insumo_id'], detalle['cantidad'], 
                 detalle['stock_actual'], nuevo_stock, current_user.id,
                 f"Orden de compra #{orden_id}"))
        
        # Cambiar estado de orden
        cursor.execute("UPDATE ordenes_compra SET estado = 'Recibida' WHERE id = %s", (orden_id,))
        db.database.commit()
        
        flash("Orden recibida y stock actualizado correctamente", "success")
        
    except Exception as e:
        db.database.rollback()
        flash(f"Error al recibir orden: {str(e)}", "danger")
    finally:
        cursor.close()
    
    return redirect(url_for('listar_ordenes_compra'))


# ------------------------------------------------------------
# VER MOVIMIENTOS DE UN INSUMO
# ------------------------------------------------------------
@app.route('/inventario/insumos/<int:insumo_id>/movimientos')
@login_required
@role_required('bodega', 'farmacia', 'administrador')
def ver_movimientos(insumo_id):
    """Ver historial de movimientos de un insumo"""
    cursor = db.database.cursor(dictionary=True)
    
    try:
        # Datos del insumo
        cursor.execute("""
            SELECT i.*, c.nombre as categoria_nombre, p.nombre as proveedor_nombre
            FROM insumos i
            LEFT JOIN categorias_insumos c ON i.categoria_id = c.id
            LEFT JOIN proveedores p ON i.proveedor_id = p.id
            WHERE i.id = %s
        """, (insumo_id,))
        insumo = cursor.fetchone()
        
        if not insumo:
            flash("Insumo no encontrado", "danger")
            return redirect(url_for('listar_insumos'))
        
        # Movimientos
        cursor.execute("""
            SELECT m.*, u.nombre as usuario_nombre
            FROM movimientos_inventario m
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.insumo_id = %s
            ORDER BY m.fecha DESC
        """, (insumo_id,))
        movimientos = cursor.fetchall()
        
    except Exception as e:
        flash(f"Error al cargar movimientos: {str(e)}", "danger")
        return redirect(url_for('listar_insumos'))
    finally:
        cursor.close()
    
    return render_template('modulos/inventarios/movimientos.html',
                         insumo=insumo,
                         movimientos=movimientos)


if __name__ == '__main__':
    app.run(port=4000, host='0.0.0.0', debug=True)


