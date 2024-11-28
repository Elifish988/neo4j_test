from flask import jsonify


class PhoneRepository:
    def __init__(self, driver):
        self.driver = driver

    def create_phone(self, phone_data):
        with self.driver.session() as session:
            for device in phone_data['devices']:
                session.run("""
                    MERGE (d:Device {id: $id})
                    SET d.brand = $brand, d.model = $model, d.os = $os,
                        d.latitude = $latitude, d.longitude = $longitude,
                        d.altitude_meters = $altitude_meters, d.accuracy_meters = $accuracy_meters
                """, {
                    "id": device['id'],
                    "brand": device['brand'],
                    "model": device['model'],
                    "os": device['os'],
                    "latitude": device['location']['latitude'],
                    "longitude": device['location']['longitude'],
                    "altitude_meters": device['location']['altitude_meters'],
                    "accuracy_meters": device['location']['accuracy_meters']
                })

            # Create the interaction relationship
            interaction = phone_data['interaction']
            session.run("""
                MATCH (from:Device {id: $from_device}), (to:Device {id: $to_device})
                MERGE (from)-[r:CONNECTED]->(to)
                SET r.method = $method, r.bluetooth_version = $bluetooth_version,
                    r.signal_strength_dbm = $signal_strength_dbm, r.distance_meters = $distance_meters,
                    r.duration_seconds = $duration_seconds, r.timestamp = $timestamp
            """, {
                "from_device": interaction['from_device'],
                "to_device": interaction['to_device'],
                "method": interaction['method'],
                "bluetooth_version": interaction['bluetooth_version'],
                "signal_strength_dbm": interaction['signal_strength_dbm'],
                "distance_meters": interaction['distance_meters'],
                "duration_seconds": interaction['duration_seconds'],
                "timestamp": interaction['timestamp']
            })

        # Return a success message
        return {"message": "Data added successfully"}



    def find_bluetooth_sequences(self):
            try:
                with self.driver.session() as session:
                    result = session.run("""
                         MATCH (d:Device)
                         OPTIONAL MATCH path = (d)-[:CONNECTED*..15 {method: 'Bluetooth'}]->(other)
                         WITH collect(nodes(path)) AS all_paths
                         UNWIND all_paths AS group
                         WITH DISTINCT group WHERE size(group) > 1
                         RETURN [node IN group | {id: node.id, brand: node.brand, model: node.model}] AS devices, size(group) AS path_length
                     """)

                    sequences = [
                        {
                            "devices": record["devices"],
                            "path_length": record["path_length"]
                        }
                        for record in result
                    ]

                    return jsonify(sequences), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def find_signal_strength_dbm(self):
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (c:Device)-[r:CONNECTED]->(other_device)
                    WHERE r.signal_strength_dbm > -60
                    RETURN c, r, other_device
                """)

                sequences = [
                    {
                        "from_device": record["c"].id,
                        "to_device": record["other_device"].id,
                        "signal_strength_dbm": record["r"]["signal_strength_dbm"],
                        "timestamp": record["r"]["timestamp"]
                    }
                    for record in result
                ]

                return jsonify(sequences), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    def devic_connections_by_ID(self, id):
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Device)-[:CONNECTED]->(n2:Device)
                    WHERE n2.id = 	$id
                    RETURN COUNT(*) AS num_connections
                """, {"id": id})

                result_data = [record["num_connections"] for record in result]
                return jsonify(result_data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

