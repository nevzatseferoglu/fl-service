# fl-service

## Success Criteria

- Manuel installation versus, saas installation time improvement will be %70.
- At least 4 client + 1 server.
- Face detection algorithm will run at 80% accuracy and new data will improve to 85% percent.

## Architecture

![0.1.0](./assets/architecture.png)


## Plannings

- Add `ad-hoc` support which wraps the certain operation by doing ad-hoc call to certain hosts.
- Report missing methods documentations to official repository.
- Check out how Depedens work.


## Extra linting

- pyright --outputjson . | jq '.summary | {errorCount, warningCount} | values'


## ToDo

- Change database in a way that it can manage more than one fl algorithm. That mean there will be more than one (server/clients) configuration
- Change database type to client/server arch
- Update architecture diagram
- Draw sequence diagram
- Documentation
- Setting request path, query parameters validation rules
