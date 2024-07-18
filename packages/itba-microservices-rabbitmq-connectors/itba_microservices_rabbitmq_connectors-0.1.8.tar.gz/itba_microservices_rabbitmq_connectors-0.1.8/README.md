# Project Documentation

This project is designed as a comprehensive learning exercise in building a fully operational microservices architecture.

- **Microservices Architecture**: Structuring applications as a collection of loosely coupled services.
- **Automated Testing**: Implementing various types of tests (unit, integration, end-to-end, and security) to ensure code quality and robustness.
- **CI/CD Pipeline**: Integrating continuous integration and continuous deployment pipelines to automate the build, test, and deployment processes.
- **Cloud Deployment**: Deploying the application to cloud infrastructure using Kubernetes and Helm for scalable and reliable operations.

## Business idea 

The specific application developed as part of this project is an AI chat platform. The platform allows teachers to upload topics to a database, enabling students to ask questions and receive answers on various subjects. While the functionality of the AI chat platform is important, it serves as a secondary objective to the primary goal of mastering microservices architecture and its associated technologies and practices.

## Domain design
![Domains](dominios.png)

## Implementation design
![Domains](dominios.png)


## Design Decisions
- **Decoupled New Message Transactions**: Implemented using RabbitMQ queues to ensure asynchronous processing and improve scalability.
- **Isolated Repeated Code Modules**: Created self-made artifacts, deployed to PyPI, and consumed as dependencies in upstream microservices to avoid code duplication and enhance maintainability.

## Application Level
- **FastAPI**: Backend framework for building web APIs.
- **RabbitMQ**: Message broker used for handling message queues.
- **Postgres**: Relational database management system.
- **ReactJS**: Frontend library for building user interfaces.

## Testing
- **Pre-commit Checks**: Automated checks to ensure code quality before committing changes.
- **Unit Tests**: Using PyTest and Mocks for isolated testing of individual components.
- **Integration Tests**: 
  - PyTest and ad hoc scripting used to verify the interaction between microservices and RabbitMQ.
  - Tested artifact integration with RabbitMQ.
  - Tested microservice integration with Postgres.
  - Tested microservice API Gateway integration with call relays.
- **End-to-End Tests**: Using Tavern for comprehensive testing of the entire application workflow.
- **Security Testing**: Static analysis using Bandit to identify potential security vulnerabilities in the codebase.

## Infrastructure
- **Deployable to Kubernetes**: Using Helm charts for easy deployment and management.
  - **Local Deployment**: With Minikube, using the command `helm install itba-7340-g2 /helm`.
  - **AWS EKS Deployment**: Supports deployment to AWS Elastic Kubernetes Service (EKS) via CI/CD pipeline.

## CI/CD
- **GitLab Actions**: CI/CD pipelines configured to automate the build, test, and deployment processes.
- **Docker Images**: 
  - Builds various Docker images for artifacts, intermediary stages, production, and testing.
- **Testing Pipeline**: 
  - Applies different types of testing (unit, integration, end-to-end).
- **Artifact Delivery**: 
  - If tests pass, Docker images and PyPI artifacts are delivered.
- **Deployment**: 
  - Proceeds to deploy the application to the production environment upon successful testing.

## Local repository configuration

Install pre-commit tool via pip. 

```
pip install pre-commit
pre-commit install
pre-commit run --all-files
```
## Authors
- Gonzalo Beade - [gbeade@itba.edu.ar](mailto:gbeade@itba.edu.ar)
- Gaspar Budo Berra - [gbudoberra@itba.edu.ar](mailto:gbudoberra@itba.edu.ar)
- Gonzalo Rossin - [grossin@itba.edu.ar](mailto:grossin@itba.edu.ar)

## License
Completely open