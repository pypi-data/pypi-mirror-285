# SimpleColorLogger

SimpleColorLogger is a simple Python package for printing colored log messages to the terminal.

## Installation

```bash
pip install SimpleColorLogger
```

## Usage

```python
from simplecolorlogger.logger import ColorLogger, Color

ColorLogger.log("This is a normal log message.")
ColorLogger.log("This is a log message with a custom color.", Color.YELLOW)
ColorLogger.info("This is an info message.")
ColorLogger.success("This is a success message.")
ColorLogger.warning("This is a warning message.")
ColorLogger.error("This is an error message.")
```

## Feature Requests
I initially created this repository for personal use, but decided to share it publicly. 
If you have any suggestions, such as additional colors, please feel free to email me at info@music-request.com or submit a request directly in this repository on GitHub.


## License
This project is licensed under the MIT License.