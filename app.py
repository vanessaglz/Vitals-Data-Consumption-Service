from vitals_data_retrieving.vitals_data_retrieving_controller import vitals_data_retrieving_api
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from algorithm_profiler import performance_bp
import os

app = Flask(__name__)
app.register_blueprint(performance_bp, url_prefix='/metrics')
cors = CORS(app, resources={r"/vitals_data_retrieving/*": {"origins": "*"}})

if os.path.exists('.env'):
    load_dotenv()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.environ.get('APP_SECRET_KEY')

app.register_blueprint(vitals_data_retrieving_api, url_prefix='/vitals_data_retrieving')

@app.route('/')
def home():
    return jsonify({
        'status': 'API is running',
        'endpoints': {
            'vitals': '/vitals_data_retrieving/'
        }
    })

if __name__ == '__main__':
    #app.run(debug=True)
    #app.run(host="0.0.0.0", port=5000, debug=False)
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('ENVIRONMENT', 'development') == 'development'
    # Evita múltiples registros de blueprints por reloader:
    use_reloader = False if debug else False
    app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)
