from flask import Blueprint, request, jsonify

from neo4j_init import neo4j_driver
from servis import PhoneRepository

phone_blueprint = Blueprint('phone_blueprint', __name__)


@phone_blueprint.route("/api/phone_tracker", methods=['POST'])
def get_interaction():
    try:
        phone_data = request.get_json()
        if not phone_data:
            return jsonify({"error": "No data provided"}), 400

        repository = PhoneRepository(neo4j_driver)
        result = repository.create_phone(phone_data)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phone_blueprint.route("/api/bluetooth_sequences", methods=['GET'])
def find_bluetooth_sequences():
    repository = PhoneRepository(neo4j_driver)
    return repository.find_bluetooth_sequences()

@phone_blueprint.route("/api/signal_strength_dbm", methods=['GET'])
def find_signal_strength_dbm():
    repository = PhoneRepository(neo4j_driver)
    return repository.find_signal_strength_dbm()


@phone_blueprint.route("/api/devic_connections_by_ID/<string:id>", methods=['GET'])
def devic_connections_by_ID(id):
    repository = PhoneRepository(neo4j_driver)
    return repository.devic_connections_by_ID(id)



@phone_blueprint.route("/api/two_devices_connected", methods=['GET'])
def two_devices_connected():
    data = request.get_json()
    repository = PhoneRepository(neo4j_driver)
    return repository.two_devices_connected(data)



@phone_blueprint.route("/api/find_Last_connection/<string:id>", methods=['GET'])
def find_Last_connection(id):
    repository = PhoneRepository(neo4j_driver)
    return repository.find_Last_connection(id)
