# refinance
![logo](docs/refinance-logo.jpg)

refined financial system for a hackerspace. simple by design.

## architecture

### entity
anything that can send or receive money: human, donate-box, rent, utility.

### transaction
move X from A to B. supports all currencies.
- non-confirmed
- confirmed

### balance
sum of all transactions. both confirmed and not. separated.

### tags
mark entities and transactions for quick search.

## authentication
- you can request a login link with your entity name, telegram id, signal id or whatever.
- login link will be sent to all available destinations (telegram, signal, email, etc)
- new login link does not revoke old ones, so no one can deauthenticate you. 

## production
put secrets into `secrets.env`. see `secrets.env.example` as a reference. 

```console
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
API: http://0.0.0.0:8000/docs
UI: http://0.0.0.0:9000

## development

### create local environment with all dependencies
```console
uv python install 3.12
uv sync --dev
```

open project in vscode, <kbd>F1</kbd> `python.setInterpreter`, select `.venv` (workspace)

if you need to change project deps:
```console
uv add packagename
uv lock
uv export > requirements.txt
cp requirements.txt ui
cp requirements.txt api
```

### tests
```
docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api pytest
```

### run backend & frontend with live code reload
```
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```
open http://localhost:8000/docs and http://localhost:9000

## todo
- [x] base classes
- [x] errors
- [x] unit tests
- [x] complex search
- [x] pagination
- [x] tags
- [x] transactions
- [x] balances
- [x] balance cache
- [x] date range search
- [ ] recurrent payments
- [ ] donation categories (entities?)
- [ ] migrations (not alembic?)
- [ ] logging
- [x] docker
- [ ] grafana, statistics
- [x] authentication?
- [ ] permissions?
- [x] pytest ci
- [ ] easy payment urls
- [ ] card processing
- [ ] currency exchange

### techdebt
- [x] fix parameters override with function signature redeclaration in services
- [ ] add reserved entities, id ranges and bootstrapping

## tests notice
tests are mostly autogenerated by llm, given the route and schema. human review would be beneficial. 

## license
MIT
