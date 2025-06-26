from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Хранилище данных в памяти
sensors = []
next_id = 1


@app.route('/sensors', methods=['GET'])
def get_all_sensors():
    return jsonify([{
        'id': s['id'],
        'type': s['type'],
        'location': s['location'],
        'last_value': s['last_value'],
        'status': s['status'],
        'last_updated': s['last_updated']
    } for s in sensors])


@app.route('/sensors/online', methods=['GET'])
def get_online_sensors():
    online_sensors = [s for s in sensors if s['status'] == 'online']
    return jsonify([{
        'id': s['id'],
        'type': s['type'],
        'location': s['location'],
        'last_value': s['last_value'],
        'last_updated': s['last_updated']
    } for s in online_sensors])


@app.route('/sensors/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    sensor = next((s for s in sensors if s['id'] == sensor_id), None)
    if not sensor:
        return jsonify({'error': 'Sensor not found'}), 404
    return jsonify(sensor)


@app.route('/sensors', methods=['POST'])
def register_sensor():
    global next_id
    data = request.json

    # Валидация обязательных полей
    required_fields = ['type', 'location', 'last_value']
    if not data or any(field not in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Валидация значений
    if not isinstance(data['last_value'], (int, float)):
        return jsonify({'error': 'last_value must be a number'}), 400

    # Установка значений по умолчанию
    status = data.get('status', 'offline')
    last_updated = data.get('last_updated', datetime.utcnow().isoformat() + 'Z')

    new_sensor = {
        'id': next_id,
        'type': data['type'],
        'location': data['location'],
        'last_value': float(data['last_value']),
        'status': status,
        'last_updated': last_updated
    }

    sensors.append(new_sensor)
    next_id += 1
    return jsonify(new_sensor), 201


@app.route('/sensors/<int:sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    global sensors
    initial_count = len(sensors)
    sensors = [s for s in sensors if s['id'] != sensor_id]

    if len(sensors) == initial_count:
        return jsonify({'error': 'Sensor not found'}), 404
    return jsonify({'message': f'Sensor {sensor_id} deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)