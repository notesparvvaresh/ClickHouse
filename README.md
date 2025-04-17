
## 🚀 آشنایی با ClickHouse و لاگ‌گیری با پایتون

### 🧠 ClickHouse چیست؟

**ClickHouse** یک دیتابیس ستونی (column-oriented) و متن‌باز است که توسط شرکت **Yandex** توسعه یافته. این سیستم برای تحلیل سریع داده‌های حجیم طراحی شده و در دسته دیتابیس‌های **OLAP** (تحلیلی) قرار می‌گیرد.

### ✅ ویژگی‌های کلیدی:

- **ذخیره‌سازی ستونی**: خواندن داده‌های بزرگ فقط از ستون‌های مورد نیاز
- **بسیار سریع** در تحلیل‌های پیچیده روی میلیون‌ها یا میلیاردها ردیف
- **مقیاس‌پذیری بالا**: امکان استفاده به‌صورت توزیع‌شده (Distributed)
- **پشتیبانی از SQL**: با دستورات SQL می‌توان کوئری‌های تحلیلی اجرا کرد
- مناسب برای کاربردهایی مثل تحلیل لاگ‌ها، مانیتورینگ، داشبوردهای real-time و…

---

## 🔎 معماری کلی و جزئیات فنی

### 📦 ساختار داده:

- داده‌ها به‌صورت ستونی ذخیره می‌شوند، نه سطری
- باعث کاهش I/O و افزایش سرعت در تحلیل‌های آماری می‌شود
- دارای انواع داده مختلف مانند `String`, `Int`, `Float`, `DateTime`, و `LowCardinality`

### 🛠️ Storage Engine پرکاربرد:
- `MergeTree`: رایج‌ترین و قدرتمندترین موتور ذخیره‌سازی که ایندکس و فشرده‌سازی دارد.
- `Log`, `TinyLog`: ساده و سریع، مناسب برای تست یا بار کم

---


## 🛠️ نصب ClickHouse در لینوکس (Ubuntu/Debian)

```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E0C56BD4
echo "deb http://repo.clickhouse.com/deb/stable/ main/" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt update
sudo apt install clickhouse-server clickhouse-client -y
```

### 📦 شروع به کار:

```bash
sudo systemctl start clickhouse-server
sudo systemctl enable clickhouse-server
```

### تست اتصال:

```bash
clickhouse-client
```

---

## 👤 ساخت یوزر اختصاصی (مثلاً `reza`)

فایل تنظیمات:

```bash
sudo nano /etc/clickhouse-server/users.xml
```

و اینو به `<users>` اضافه کن:

```xml
<reza>
    <password>1234</password>
    <networks>
        <ip>::/0</ip>
    </networks>
    <profile>default</profile>
    <quota>default</quota>
</reza>
```

🔁 سپس ری‌استارت:

```bash
sudo systemctl restart clickhouse-server
```

و اتصال با یوزر:

```bash
clickhouse-client --user reza --password
```

---




## 📘 ساخت جدول لاگ در ClickHouse

برای ذخیره لاگ‌ها، ابتدا باید جدولی مطابق ساختار مورد نیاز بسازیم. مثال:

```sql
CREATE TABLE logs (
    timestamp DateTime DEFAULT now(),
    level String,
    message String,
    module String,
    function String,
    service String
) ENGINE = MergeTree()
ORDER BY timestamp;
```

---

## 🧪 ذخیره لاگ با پایتون (روش ساده)

ابتدا کتابخانه‌ی اتصال را نصب می‌کنیم:

```bash
pip install clickhouse_driver
```

و سپس یک تابع ساده برای ارسال لاگ به ClickHouse:

```python
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

```

---

## 🧰 استفاده از لاگر استاندارد پایتون (`logging`) + ارسال لاگ به ClickHouse

برای سیستم‌های واقعی، بهتره لاگ‌ها از طریق ماژول استاندارد `logging` مدیریت و ارسال بشن:

```python
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

```
