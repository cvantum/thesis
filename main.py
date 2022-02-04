# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import json
from joblib import load
from pandas import DataFrame

import tensorflow as tf
from tensorflow import keras

from confluent_kafka import Consumer

features = [
    ' Destination Port',
    ' SYN Flag Count',
    ' RST Flag Count',
    ' PSH Flag Count',
    ' ACK Flag Count'
]

if __name__ == '__main__':

    preprocess = load(open('preprocessor.pkl', 'rb'))
    model = keras.models.load_model('ids-model.h5')

    c = Consumer({
        'bootstrap.servers': '192.168.178.201:9092',
        'group.id': 'test-consumer-group'
    })

    c.subscribe(['suricata-events'])

    while True:
        msg = c.poll(1.0)

        if msg == None:
            continue
        if msg.error():
            print('Consumer error {}'.format(msg.error()))

        suricata_events = msg.value().decode('utf-8')
        suricata_json = json.loads(suricata_events)

        #tf_data = [0, 0, 0, 0, 0, 0, 0, 0]
        tf_data = [0, 0, 0, 0, 0]
        if "dest_ip" in suricata_json:
            if "0.0.0.0" in suricata_json['dest_ip'] or "f" in suricata_json['dest_ip'] or "192.168.178." in suricata_json['dest_ip'] or "255.255.255.255" in suricata_json['dest_ip']:
                continue
            else:
                if "netflow" in suricata_json:
                    #tf_data[0] = suricata_json['netflow']['min_ttl']
                    #tf_data[1] = suricata_json['netflow']['bytes']
                    pass
                else:
                    #tf_data[0] = 0
                    #tf_data[1] = 0
                    pass

                if "tcp" in suricata_json:
                    if "fin" in suricata_json['tcp']:
                        #tf_data[2] = 1
                        pass
                    else:
                        #tf_data[2] = 0
                        pass

                    if "ack" in suricata_json['tcp']:
                        tf_data[4] = 1
                    else:
                        tf_data[4] = 0

                    if "rst" in suricata_json['tcp']:
                        tf_data[2] = 1
                    else:
                        tf_data[2] = 0

                    if "psh" in suricata_json['tcp']:
                        tf_data[3] = 1
                    else:
                        tf_data[3] = 0

                    if "syn" in suricata_json['tcp']:
                        tf_data[1] = 1
                    else:
                        tf_data[1] = 0

                    tf_data[0] = suricata_json['dest_port']
                    dataframe = DataFrame([tf_data], columns=features)
                    X = preprocess.transform(dataframe)
                    #print(X)
                    predict = model.predict(X)
                    if predict > 0.5:
                        print(predict)
                        print(suricata_json['src_ip'])
                        print(suricata_json['dest_ip'])
                        print(suricata_json['dest_port'])

        else:
            #print(suricata_json)
            continue
    c.close()