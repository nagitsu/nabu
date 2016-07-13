# nabu

## Requirements

* Python 3.4.3
* [Elasticsearch](https://www.elastic.co/products/elasticsearch) 1.5.2

We also need to install some system packages:
```bash
sudo apt-get install postgresql-9.4 postgresql-server-dev-9.4 redis-server openblas openblas-dev
sudo apt-get build-dep python-lxml
```

## How to deploy

* Clone the repo
* Create a [virtualenv](https://virtualenv.pypa.io/en/stable/) for the project:
```bash
$ pip install virtualenv
$ mkdir virtualenv
$ virtualenv virtualenv/ --python=/usr/bin/python3
```
* Install the requirements file:
```bash
python install -r deploy/requirements.txt
```
* Setup the database
```bash
$ sudo -u postgres createuser nabu -s
$ createdb nabudb -E UTF8 -T template0
```

## How to run

* Run the application dependencies:
```
$ redis-server
$ sudo service elasticsearch start
```
* Run the application components, don't forget to activate the `virtualenv` (`source virtualenv/bin/activate`):
```
$ NABU_DEV='DEV' python manage.py serve
$ cd ui-nabu/dist && python3 -m http.server
$ celery worker -A nabu.vectors.tasks -c 1 -Q testing --loglevel=info -n testing@localhost
$ celery worker -A nabu.vectors.tasks -c 1 -Q training --loglevel=info -n training@localhost
```
Finally, the application should be running at [http://localhost:8000](http://localhost:8000).
