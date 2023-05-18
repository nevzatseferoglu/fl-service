
# fl-service

API which tailored to the needs of data scientists. The interface streamlines communication with remote hosts through the use of service endpoints, allowing for seamless API-based interactions. These endpoints empower users to initiate, terminate, and manage flower federated learning clusters, ensuring the preservation of a unified strategy across the system's architecture.

API documentation: https://fl-service-api-doc.netlify.app/

![0.1.0](./assets/architecture.png)

## ToDo

- [x] Change the database in a way that it can manage more than one fl algorithm. That means there will be more than one (server/clients) configuration.
- [x] Update architecture diagram
- [ ] Add diagrams (sequence)
- [ ] Set request path, query parameters validation.
- [ ] Introduce usa-case scenario and set up instructions of the host machine.
- [ ] Incrase observability.
- [ ] Add missing informations to the doc.

## Research

- [ ] Integration of middleware.
- [ ] API security.
- [ ] Making appropriate operations async.
- [ ] Realtime feedback from the endpoints.

## Success Criteria

- Manuel installation versus, saas installation time improvement will be %70.
- At least 4 client + 1 server.
- Face detection algorithm will run at 80% accuracy and new data will improve to 85% percent.

### Linting

pyright --outputjson . | jq '.summary | {errorCount, warningCount} | values'

