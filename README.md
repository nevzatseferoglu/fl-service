# fl-service

## Success Criteria

- Manuel installation versus, saas installation time improvement will be %70.
- At least 4 client + 1 server.
- Face detection algorithm will run at 80% accuracy and new data will improve to 85% percent.
- Hello

## Architecture

![0.1.0](./assets/architecture.png)


## ToDo

- Add `ad-hoc` support which wraps the certain operation by doing ad-hoc call to certain hosts.
- Report missing methods documentations to official repository.


## Extra linting

- pyright --outputjson . | jq '.summary | {errorCount, warningCount} | values'
