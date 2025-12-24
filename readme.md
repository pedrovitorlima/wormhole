* create an environment with python3 -m venv wormhole-env (skip if you are deploying)
* activate the environment with source wormhole-env/bin/activate (skip if you are deploying)
* create environment files (use .bkp as reference)
* build containers with env file `docker compose --env-file .dockerenv build`
* run the containers with `docker compose --env-file .dockerenv up`