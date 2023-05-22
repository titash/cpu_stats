from flask import Flask, jsonify,render_template
import psutil
import time
from threading import Thread

app = Flask(__name__)

def get_cpu_temperature():
    temperature = psutil.sensors_temperatures()
    if 'coretemp' in temperature:
        return temperature['coretemp'][0].current
    else:
        return None

def get_cpu_usage():
    cpu_percent  = psutil.cpu_percent(interval=3, percpu=True)
    cpu_usage = {f'Core {i+1}': percent for i, percent in enumerate(cpu_percent)}
    return jsonify(cpu_percent=cpu_usage)

def publish_temperature():
    while True:
        temperature = get_cpu_temperature()
        if temperature is not None:
            print(f"CPU Temperature: {temperature}")
            # Perform additional actions here to publish the temperature
        time.sleep(5)

@app.route('/')
def home():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append((rule.rule, rule.endpoint))

    return render_template('home.html', routes=routes)

@app.route('/cpu_temperature', methods=['GET'])
def cpu_temperature():
    temperature = get_cpu_temperature()
    if temperature is not None:
        return jsonify({'temperature': temperature})
    else:
        return jsonify({'error': 'Unable to retrieve CPU temperature'})

@app.route('/cpu_usage', methods=['GET'])
def cpu_usage():
    cpu_usage = get_cpu_usage()
    if cpu_usage is not None:
        return cpu_usage
    else:
        return jsonify({'error': 'Unable to retrieve CPU usage'})

if __name__ == '__main__':
    # Start a separate thread to continuously publish the CPU temperature
    thread = Thread(target=publish_temperature)
    thread.start()

    # Run the Flask API
    app.run(debug=True, host='0.0.0.0', port=8080)
