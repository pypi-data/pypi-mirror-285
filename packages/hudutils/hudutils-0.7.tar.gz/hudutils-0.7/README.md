Sure! Here is the updated `README.md` including the configuration file setup:

```markdown
# HudUtils

Regularly used utils.

## Installation

```bash
pip install hudutils
```

## Usage

### Flatten JSON

```python
from hudutils import hudutils

json_data = {
    "a": 1,
    "b": {
        "c": 2,
        "d": {
            "e": 3
        }
    }
}

flattened = hudutils.flatten_json(json_data)
print(flattened)
```

### Filename with Rollover

```python
from hudutils import hudutils

filename = 'log.txt'
new_filename = hudutils.filename_with_rollover(filename, opts=['year', 'month', 'day'])
print(new_filename)
```

### Elasticsearch Data Fetcher

#### Configuration File

Create a `config.json` file with the following content:

```json
{
    "base_url": "https://c6a.reseabus.com",
    "auth": ["script", "P#ssw9654321"],
    "batch_size": 5,
    "sequence_file": "test_tracker.txt"
}
```

#### Usage

```python
from hudutils import ElasticsearchDataFetcher

# Assuming you have a config file named config.json
fetcher = ElasticsearchDataFetcher('config.json')

# Fetch data from Elasticsearch
data = fetcher.fetch_data('your_index')
print(data)

# Run a specific query
query_data = fetcher.run_query('your_index', 'your_query')
print(query_data)

# Send data to Elasticsearch
docs = [{'field': 'value'}, {'field': 'value2'}]
fetcher.send_to_elasticsearch(docs, 'your_index')
```

This updated `README.md` provides clear examples of how to use the `flatten_json`, `filename_with_rollover`, and `ElasticsearchDataFetcher` functionalities within the `hudutils` library.
```

