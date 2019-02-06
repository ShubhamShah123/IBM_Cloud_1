from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json

app = Flask(__name__, static_url_path='')

db_name = 'quiz1_db'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif "CLOUDANT_URL" in os.environ:
    client = Cloudant(os.environ['CLOUDANT_USERNAME'], os.environ['CLOUDANT_PASSWORD'], url=os.environ['CLOUDANT_URL'], connect=True)
    db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def root():
    return app.send_static_file('index.html')

# @app.route('/get_all_members', methods=['GET'])
# def get_visitor():
#     print("--- get visitor ---")
#     if client:
#         to_send_list = list(map(lambda doc: doc, db))
#         return jsonify({'status': to_send_list}), 200
#     else:
#         print('No database')
#         return jsonify({'status': 'No Database'}), 400


@app.route('/get_single_member', methods = ['POST'])
def get_member():
    if client:
        user = request.get_json()
        name = user['name']
        to_send_data = []
        all_user_data = map(lambda doc: doc, db)
        for x in all_user_data:
            if name == str(x['Picture']) or str(x['Picture']).startswith(name):
                send_dict = {}
                img_name = str(x['Picture'])
                size = float(x["_attachments"][img_name]["length"])
                size_data = str(float(size/1000)) + " kb."
                send_dict = {
                    'name': img_name,
                    'size': size_data
                }
                to_send_data.append(send_dict)
            else:
                pass
        return jsonify({'status': to_send_data}), 200
    else:
        return jsonify({'status': 'Not Working'}), 400

@app.route('/get_names', methods = ['GET'])
def get_names():
    print("---- get names of all ----")
    if client:
        all_user_data = map(lambda doc: doc, db)
        to_send_list = []
        for x in all_user_data:
            if str(x['Room']) == "":
                pass
            else:
                to_send_list.append(str(x['Room']))
        return jsonify({'status': to_send_list}), 200
    else:
        return jsonify({'status': 'Not Working'}), 400


@app.route('/get_image_data', methods=['POST'])
def get_image():
    print("---- get image data ---")
    data = request.get_json()
    room_num = data['room']
    if client:
        to_send_list = []
        all_user_data = map(lambda doc: doc, db)
        for x in all_user_data:
            if str(room_num) == str(x['Room']):
                if x['Picture'] == "":
                    val = 'No Image Available'
                    
                else:
                    val = 'Image Available: {0}'.format(x['Picture'])
                    
                user_data = {
                    'image': val
                }
                to_send_list.append(user_data)
            else:
                pass
        return jsonify({'status': to_send_list}), 200

@app.route('/get_users_data', methods=['POST'])
def get_users():
    data = request.get_json()
    from_num = data['from']
    to_num = data['to']
    city = data['city']
    print("--- get users data ---")
    count = 1
    to_send_list = []
    if client:
        all_users_data = list(map(lambda doc: doc, db))
        for x in all_users_data:
            user_data = {}
            if x['Room'] >= int(from_num) and x['Room'] <= int(to_num):
                if x['City'] == city:
                    print x['Grade'],":YES : ",count
                    count += 1
                    if x['Picture'] == "":
                        val = 'No Image Available'
                        
                    else:
                        val = 'Image Available: {0}'.format(x['Picture'])
                        
                    user_data = {
                        'name': x['Name'],
                        'image': val,
                        'city_name': x['City']
                    }
                    to_send_list.append(user_data)
            else:
                print x['Grade'],":NO"
            print "-------------------------"
        return jsonify({'status': to_send_list}), 200
    else:
        print('No database')
        return jsonify({'status': 'No Database'}), 400

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
