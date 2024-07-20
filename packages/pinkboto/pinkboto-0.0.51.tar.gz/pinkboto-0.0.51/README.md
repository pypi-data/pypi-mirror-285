# pinkboto

A Colorful AWS SDK wrapper for Python

[![Current version at PyPI](https://img.shields.io/pypi/v/pinkboto.svg)](https://pypi.python.org/pypi/pinkboto)
![Supported Python Versions](https://img.shields.io/pypi/pyversions/pinkboto.svg)
![Software status](https://img.shields.io/pypi/status/pinkboto.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dd/pinkboto)

## Install

```bash
pip install pinkboto
```

### Usage

```python
import pinkboto
aws = pinkboto.aws(profile='production', region='us-east-1') 
selector = {'resource': 'aws_db_instance'}
projection = ['DBInstanceIdentifier', 'Endpoint']
rds = aws.find(selector, projection)
```

### Caching

By default, pinkboto caching all requests with 120 seconds lifespan.

To disable:

```python
aws = pinkboto.aws(profile='production', region='us-east-1', cache=False)
```

To modify lifespan to 1 hour:

```python
aws = pinkboto.aws(profile='production', region='us-east-1', cache=3600)
```

### AWS Lambda usage
When using pinkboto in an AWS Lambda it is important to change the cache folder
to the /tmp writable folder.

```python
aws = pinkboto.aws(profile='production', region='us-east-1', cache=3600, cache_folder='/tmp/pinkboto')
```

### Subfield projection

You can access a subfield in projection. For example 'Endpoint.Address' in rds

```python
rds = aws.find({'resource': 'aws_db_instance'}, ['Endpoint.Address', 'AvailabilityZone'])
```

### CSV output

```python
pinkboto.to_csv(rds, 'result.csv')
```

### pypi package publish

```bash
update setup.py version.
python3 setup.py sdist
twine upload dist/pinkboto-${new-version}.tar.gz
```

### Contributing

Pull requests for new features, bug fixes, and suggestions are welcome!

### License

GNU General Public License v3 (GPLv3)

### Developer install requirements

```bash
pre-commit install
```
