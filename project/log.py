import logging
from datetime import datetime
from clickhouse_driver import Client

# Connect to ClickHouse using clickhouse-driver
client = Client(host='localhost', user='default', password='', database='default')

class ClickHouseLogHandler(logging.Handler):
    def __init__(self, service_name):
        super().__init__()
        self.service = service_name

    def emit(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'service': self.service
        }
        try:
            # Insert log into ClickHouse
            client.execute('INSERT INTO logs (timestamp, level, message, module, function, service) VALUES', [
                (
                    log_entry['timestamp'],
                    log_entry['level'],
                    log_entry['message'],
                    log_entry['module'],
                    log_entry['function'],
                    log_entry['service']
                )
            ])
        except Exception as e:
            print(f"Error writing log to ClickHouse: {e}")

# Set up the logger
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Add handler to the logger
ch_handler = ClickHouseLogHandler(service_name="my_python_service")
logger.addHandler(ch_handler)

# Test logging
logger.info("Starting the program")
logger.warning("This is just a warning")
logger.error("This is a test error!")