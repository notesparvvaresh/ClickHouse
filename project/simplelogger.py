from clickhouse_driver import Client
from datetime import datetime

client = Client(host='localhost', user='reza', password='1234', database='default')

def log_to_clickhouse(level, message, module, function, service):
    log_entry = {
        'timestamp': datetime.now(),
        'level': level,
        'message': message,
        'module': module,
        'function': function,
        'service': service
    }

    client.execute('INSERT INTO logs (timestamp, level, message, module, function, service) VALUES', [(
        log_entry['timestamp'], 
        log_entry['level'], 
        log_entry['message'], 
        log_entry['module'], 
        log_entry['function'], 
        log_entry['service']
    )])

log_to_clickhouse('INFO', 'This is a test log', 'test_moudle', 'test_function', 'my_service')
