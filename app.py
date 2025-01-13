from vitals_data_retrieving.vitals_data_retrieving_controller import vitals_data_retrieving_api
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os


app = Flask(__name__)
cors = CORS(app, resources={r"/vitals_data_retrieving/*": {"origins": "*"}})

if os.path.exists('.env'):
    load_dotenv()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.environ.get('APP_SECRET_KEY')

app.register_blueprint(vitals_data_retrieving_api, url_prefix='/vitals_data_retrieving')

if __name__ == '__main__':
    app.run(debug=True)
