import pytest
import app


@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        # Сброс состояния перед каждым тестом
        app.sensors = []
        app.next_id = 1
        yield client
# Тесты для GET /sensors
def test_get_all_sensors_empty(client):
    response = client.get('/sensors')
    assert response.status_code == 200
    assert response.json == []

def test_get_all_sensors_with_data(client):
    client.post('/sensors', json={
        'type': 'temperature',
        'location': 'room1',
        'last_value': 25.5
    })
    response = client.get('/sensors')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['type'] == 'temperature'


# Тесты для GET /sensors/online
def test_get_online_sensors_empty(client):
    client.post('/sensors', json={
        'type': 'humidity',
        'location': 'room2',
        'last_value': 45,
        'status': 'offline'
    })
    response = client.get('/sensors/online')
    assert response.status_code == 200
    assert len(response.json) == 0


def test_get_online_sensors_with_data(client):
    client.post('/sensors', json={
        'type': 'pressure',
        'location': 'room3',
        'last_value': 1013,
        'status': 'online'
    })
    response = client.get('/sensors/online')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['type'] == 'pressure'


# Тесты для GET /sensors/{id}
def test_get_sensor_valid(client):
    response = client.post('/sensors', json={
        'type': 'light',
        'location': 'room4',
        'last_value': 350
    })
    sensor_id = response.json['id']
    response = client.get(f'/sensors/{sensor_id}')
    assert response.status_code == 200
    assert response.json['type'] == 'light'


def test_get_sensor_invalid(client):
    response = client.get('/sensors/999')
    assert response.status_code == 404
    assert response.json['error'] == 'Sensor not found'


# Тесты для POST /sensors
def test_register_sensor_valid(client):
    response = client.post('/sensors', json={
        'type': 'motion',
        'location': 'hall',
        'last_value': 0
    })
    assert response.status_code == 201
    assert response.json['id'] == 1
    assert response.json['status'] == 'offline'


def test_register_sensor_missing_field(client):
    response = client.post('/sensors', json={
        'type': 'temperature',
        'last_value': 22
    })
    assert response.status_code == 400
    assert 'error' in response.json


def test_register_sensor_invalid_value(client):
    response = client.post('/sensors', json={
        'type': 'co2',
        'location': 'lab',
        'last_value': 'high'
    })
    assert response.status_code == 400
    assert 'error' in response.json


# Тесты для DELETE /sensors/{id}
def test_delete_sensor_valid(client):
    client.post('/sensors', json={
        'type': 'noise',
        'location': 'office',
        'last_value': 65
    })
    response = client.delete('/sensors/1')
    assert response.status_code == 200
    assert len(app.sensors) == 0


def test_delete_sensor_invalid(client):
    response = client.delete('/sensors/999')
    assert response.status_code == 404
    assert response.json['error'] == 'Sensor not found'


# Дополнительные тесты
def test_online_status_filter(client):
    # Добавляем 3 сенсора: 2 онлайн, 1 офлайн
    r1 = client.post('/sensors', json={
        'type': 'temp', 'location': 'L1', 'last_value': 20, 'status': 'online'
    })
    r2 = client.post('/sensors', json={
        'type': 'hum', 'location': 'L2', 'last_value': 40, 'status': 'online'
    })
    client.post('/sensors', json={
        'type': 'pres', 'location': 'L3', 'last_value': 1000, 'status': 'offline'
    })

    response = client.get('/sensors/online')
    assert response.status_code == 200
    assert len(response.json) == 2

    # Проверяем по ID, что вернулись правильные сенсоры
    returned_ids = {s['id'] for s in response.json}
    assert returned_ids == {r1.json['id'], r2.json['id']}


def test_default_timestamp(client):
    response = client.post('/sensors', json={
        'type': 'light',
        'location': 'garden',
        'last_value': 12000
    })
    assert 'last_updated' in response.json
    assert response.json['last_updated'] != ''