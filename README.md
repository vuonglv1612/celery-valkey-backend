# Celery ValKey Backend

A custom result backend for Celery using ValKey as the storage engine. This backend provides a scalable, high-performance alternative to traditional result backends by leveraging ValKey's distributed key-value store capabilities.

## Requirements

- Python >= 3.8
- Celery >= 4.4.0
- ValKey >= 6.0.0

## Installation

Install the package using pip:

```bash
pip install celery-valkey-backend
```

## Quick Start

Use the ValKey backend in your Celery application:

```python
from celery import Celery

app = Celery('your_app', backend='valkey://localhost:6379/0')

@app.task
def add(x, y):
    return x + y

# Using the task
result = add.delay(4, 4)
print(result.get())  # Output: 8
```

## URL Format

The backend URL format:
```
valkey://host:port/db
```

Example:
```
valkey://localhost:6379/0
```

## Development

```bash
# Clone the repository
git clone https://github.com/vuonglv1612/celery-valkey-backend.git
cd celery-valkey-backend

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License.

## Support

If you encounter any problems or have questions, please open an issue on [GitHub Issues](https://github.com/vuonglv1612/celery-valkey-backend/issues).