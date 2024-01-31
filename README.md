# DysRegNetWeb

## Installation
Clone the repository
``` bash
git clone https://github.com/JohannesKersting/DysRegNetWeb.git
```

Navigate to the folder
``` bash
cd DysRegNetWeb
```

### For development and debugging

#### Launching the web app
Setup a fresh [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) environment with Python 3.8
``` bash
conda create -n DysRegNetWeb python=3.8
```

Activate the environment
``` bash
conda activate DysRegNetWeb
```

Install the required dependencies using pip
``` bash
pip install -r app/requirements.txt
```

Launch the app
``` bash
python app/app.py
```

The web app is now available under http://127.0.0.1:8050/ but the database is not running yet

### Launching the database
Open a fresh shell and navigate to the repository folder. 
Launch the Neo4j database using [Docker](https://docs.docker.com/engine/install/ubuntu/).
In order for this to work, the repository must include a folder called "data" containing the Neo4j database files.

``` bash
docker run -it --rm \
    --user "$(id -u):$(id -g)" \
    --name dysregnet-neo4j \
    -p7474:7474 -p7687:7687 \
    -v ${PWD}/data:/data \
    --env NEO4J_AUTH=neo4j/12345678 \
    neo4j:5.11.0
```
If you have user permission problems connected to `--user=$(id -u):$(id -g)`, consider omitting this.
Also, the container can be run in the background using `-d`.
``` bash
docker run -it --rm -d \
    --name dysregnet-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -v ${PWD}/data:/data \
    --env NEO4J_AUTH=neo4j/12345678 \
    neo4j:5.11.0
```

### Launching the in-menory session cache
The app [caches session data](https://dash.plotly.com/background-callback-caching) using Celery as a broker and a [Redis](https://redis.io/docs/) database.
Now start the [Redis docker official image](https://www.docker.com/blog/how-to-use-the-redis-docker-official-image/) in a similar fashion to the Neo4j container.
``` bash
docker run -it --rm -d \
    --name dysregnet-redis \
    -p 6379:6379 \
    redis:7.2.4
```
Alternatively, you can also specify the exposed redis IP more directly using e.g. `-p 127.0.0.1:6379:6379/tcp`.
Afterwards, export the IP address in the shell you are calling `python app/app.py` from.
``` bash
export REDIS_URL="redis://127.0.0.1:6379"
```
Now we need to lauch celery worker(s) in a new terminal from the location of `app.py`.
Keep in mind to use the conda environment to ensure the same software is called from terminal and the dash app.
For the celery command we need to specify which celery instance we are referring to.
That is, the variable name of our Celery instance in `app.py` (in our case `celery_broker`).
``` bash
celery --app app:celery_broker worker --loglevel=INFO --concurrency=2
```

### Test for production
Run docker compose inside the repository folder
``` bash
docker compose up -d
```



