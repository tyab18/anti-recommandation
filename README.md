# anti-recommandation
## Structure
- `api/`: API specification file (OpenAPI 3.0.3)
- `client/`: source code of client-side
- `server/`: 
  - `Dockerfile`: Dockerfile for API server
  - `docker-compose.yml`: docker-compose file for API server
  - `shared/`: source code of API server
    - `server.py`: entrypoint of API server
    - `db.sqlite3`: database for API server (not included in this repo)
    - [`BDAwork/`](https://github.com/garnet-k/BDAwork): core of API server (not included in this repo)
- `db/`: tools to generate `db.sqlite3`
  - `database.py`: a wrapper of sqlite3
  - `db-example.ipynb`: instruction to generate `db.sqlite3`
