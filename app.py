from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'

db = SQLAlchemy(app)

# Crear modelo de bases de datos
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Corregido a Integer
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(11), nullable=False)

    # Serialización
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }

# Crea las tablas en la base de datos
with app.app_context():
    db.create_all()

# Crear Rutas
@app.route('/contacts',methods=['GET'])
def get_contacts():
    contacts =Contact.query.all();
    list_contact =[];
    for contact in contacts:
        list_contact.append(contact.serialize())
    return jsonify({'contacts':list_contact})

@app.route('/contacts',methods=['POST'])
def post_contacts():
    data=request.get_json()
    contact =Contact(name=data['name'],email=data['email'],phone=data['phone'])
    db.session.add(contact);
    db.session.commit();
    return jsonify({'message':"Contacto creado con exitos",'contact':contact.serialize()}),201;

@app.route('/contacts/<int:id>',methods=['GET'])
def get_contact(id):
    contact =Contact.query.get(id)
    if not  contact:
        return jsonify({'message':'Contacto no encontrado'}),404;
    return jsonify(contact.serialize())

@app.route('/contacts/<int:id>', methods=['PUT','PATCH'])
def update_contact(id):
    contact =Contact.query.get_or_404(id);
    # El silent evita lanzar la excepcion si no hay  JSON
    data =request.get_json(silent=True)

    if data is None:
        return jsonify({'error':'No se ha proporcionado ninguno datos'}),400
    # Campos permitidos para la  actualizacion
    allowed_fields =['name','email','phone']
    # Recorremos los campos

    for field in allowed_fields:
        if field in data:
            setattr(contact,field,data[field])

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Revierte en caso de error
        return jsonify({'error': 'Error al actualizar contacto', 'details': str(e)}), 500
    return jsonify({'message': "Contacto actualizado correctamente"}), 200

@app.route('/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    try:
        # Obtener el contacto a eliminar
        contact = Contact.query.get_or_404(id)

        # Eliminar el contacto de la base de datos
        db.session.delete(contact)
        db.session.commit()

        # Retornar una respuesta exitosa con código 204 No Content
        return jsonify({'status': 'success', 'message': 'Contacto eliminado correctamente'}), 200

    # Capturar cualquier excepción que pueda ocurrir
    except Exception as e:
        # Registrar el error en los logs para facilitar la depuración
        app.logger.error(f"Error al eliminar el contacto {id}: {str(e)}")

        # Retornar una respuesta de error con código 500 Internal Server Error
        return jsonify({'status': 'error', 'message': 'Error al eliminar el contacto'}), 500
