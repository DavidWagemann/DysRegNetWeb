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

### Launching the in-menory redis cache
The app [caches session data](https://dash.plotly.com/background-callbacks) using Celery and a [Redis](https://redis.io/docs/) database.


### Test for production
Run docker compose inside the repository folder
``` bash
docker compose up -d
```



