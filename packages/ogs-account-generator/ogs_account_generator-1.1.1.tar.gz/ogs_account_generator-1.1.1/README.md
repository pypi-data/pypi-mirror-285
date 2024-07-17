# Online-Go.com Account Generator

This Python script automates the creation of accounts on Online-Go.com and joins the Doulet Media group using Selenium WebDriver.

## Installation

1. **Python Setup**: Ensure Python 3.x is installed on your system.

2. **WebDriver**: Download the WebDriver for Chrome from [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/).

3. **Dependencies**: Install required Python packages:
```sh
pip install selenium
```

## Usage

1. **Clone Repository**: Clone this repository to your local machine.

2. **Configuration**:
- Update `ra.py` with your WebDriver path and account details.

3. **Run Script**: Execute the script:
```sh
python ra.py
```


The script will automatically register accounts starting from where it left off or from the beginning if no previous state is found.

## Package

- **PyPI**: [ogs-account-generator](https://pypi.org/project/ogs-account-generator/)
```python
pip install ogs-account-generator
```

## Notes

- Ensure your system is connected to the internet during execution.
- Make sure to comply with Online-Go.com's terms of service and usage policies.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

