from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    infos = Message.query.order_by(Message.created_at.asc()).all()
    infos_list = [info.to_dict() for info in infos]

    response = make_response(
        jsonify(infos_list),
        200,
    )

    return response

@app.route('/messages/<int:id>')
def messages_by_id(id):
    info = Message.query.filter(Message.id == id).first()
    info_dict = info.to_dict()

    response = make_response(
        info_dict,
        200,
    )

    return response

@app.route('/messages', methods = ['POST'])
def new_message():
    data = request.get_json()
    
    if 'body' not in data or 'username' not in data:
        return jsonify({"error": "Bad Request", "message": "Both 'body' and 'username' are required."}), 400
    
    new_message = Message(
        body=data['body'],
        username=data['username']
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    return jsonify({
        "id": new_message.id,
        "body": new_message.body,
        "username": new_message.username,
        "created_at": new_message.created_at
    }), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    data = request.get_json()
    message = db.session.get(Message, id) 

    if message:
        if 'body' in data:
            message.body = data['body']

        db.session.commit()

        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username
        }), 200
    else:
        return jsonify({"error": "Message not found"}), 404

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)  
    
    if message:
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": "Message deleted successfully"}), 200
    else:
        return jsonify({"error": "Message not found"}), 404


if __name__ == '__main__':
    app.run(port=5555)
