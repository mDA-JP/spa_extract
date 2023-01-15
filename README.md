This script extracts spa infomation (name, address and coordinates) from ["スーパー銭湯 全国検索"](https://www.supersento.com).

## Preparation

- Use pipenv

```bash
pipenv install
```

- Use venv

```bash
python -m venv venv
source venv/bin/activate
pip install beautifulsoup4 requests
```

## Usage

```bash
python main.py > {output file name}
```
