# Glyphic AI take home test

This repository contains the implementation of a web app by Jevgenij Zubovskij for the Glyphic AI take-home test. The app allows users to ask questions about selected sales calls

## Key notes

There are several important notes that apply to the whole README/repo:

* All code blocks in this README assume the user starts executing them from the repository root folder
* If any instructions in this README contain typos or are missing details, please consult the `.github/workflows` YAML files for the commands as they contain the full automation of this project's function
* This README assumes familiarity with AWS, Terraform, and Docker concepts

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Running locally](#running-locally)
   - [Backend](#backend)
   - [Frontend](#frontend)
4. [Testing](#testing)
   - [Backend](#backend-1)
   - [E2E](#e2e)
   - [Terraform](#terraform)
     - [Frontend](#frontend-1)
     - [Backend](#backend-2)
5. [Linting](#linting)
6. [Building](#building)
   - [Backend](#backend-3)
   - [Frontend](#frontend-2)
7. [Deployment](#deployment)
   - [Backend](#backend-4)
   - [Frontend](#frontend-3)
   - [Infrastructure](#infrastructure)
8. [CI](#ci)
9. [Extra functionality](#extra-functionality)
10. [Improvements currently out of scope](#improvement-currently-out-of-scope)

## Prerequisites

Not exclusive to these versions of the software, should work with newer ones where available (not tested):

* Node version: `23.5`
* Python3 version: `3.11`
* Terraform version: `1.5.7`
* AWS CLI v2: `2.221`
* Docker: `27.3.1`

`Note`:Terraform and Docker are required for [deployment](#deployment) and infrastructure provisioning. Ensure the specified versions or later are installed

## Setup

Once all the prerequisites are installed to install all dependencies:
```bash
cd frontend && yarn install && npx playwright install && cd ..
cd backend/src && python3 -m pip install --no-cache-dir -r requirements.txt
```

## Running locally

Once all dependencies are installed the project can be run locally

### Backend
To run the backend server locally with automatic reloading when source code changes

```bash
export ANTHROPIC_API_KEY=<your-anthropic-api-key>
cd backend/src && python3 -m uvicorn --port 8000 server:app --reload
```

Without closing the terminal tab, the server is now running on port 8000 of the host machine

### Frontend

To run the frontend with the same reload on source code change. Note that `REACT_APP_API_URL` is being set here to the backend server URL

```bash
cd frontend && REACT_APP_API_URL=localhost:8000 yarn start
```

The frontend server is now accessible on port 3000 of the host machine

## Testing

### Backend

For the backend:

```bash
cd backend/src && python3 -m pytest
```

### E2E

To run the E2E test suite the backend and frontend need to be running ([see previous section](#running-locally)). After that:

```bash
cd frontend && BASE_URL=localhost:3000 npx playwright test
```

`Note`: the `BASE_URL` is being set here to point at the URL of where the frontend server is running

### Terraform 

There are two independent stacks of infrastructure, one for hosting the frontend and one for the backend. To validate/plan the stacks the commands are:

#### Frontend

```bash
cd infrastructure/frontend && terraform init
terraform validate 
terraform plan
```


#### Backend 

```bash
cd infrastructure/backend && terraform init
terraform validate 
terraform plan
```

## Linting

Frontend:

```bash
cd frontend && yarn lint --fix
```

Backend:

```bash
cd backend/src && python3 -m black .
```

Terraform

```bash
terraform fmt -recursive
```

## Building

### Backend
The backend is built into a Docker image called `glyphic-backend`, To build it run:

```bash
./backend/deployment/build.sh
```

### Frontend
The frontend is built into static webpage with the output located at `frontend/build`. To build it run:

```bash
REACT_APP_API_URL=<backend service URL> ./frontend/deployment/build.sh
```

## Deployment

`Note`: this is only applicable for account with relevant AWS IAM credentials 

Terraform gets its credentials from the environment variable, ensure       `AWS_REGION`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

Deployment is essentially done in 3 stages:

* Deploy the infrastructure (can be omitted if no changes after first application)
* Deploy the built backend to the created EKS cluster
* Deploy the built frontend to the created S3 bucket configured to serve a static website

The values relevant to note from this are:
* The URL of the statically served website
* The backend URL (built into the frontend) is currently hardcoded. However, it can be automatically acquired when the core infrastructure is created

To deploy the above parts the relevant commands are:

### Backend

```bash
./backend/deployment/push.sh
```

### Frontend

```bash
./frontend/deployment/push.sh
```

### Infrastructure

* `cd ./infrastructure/frontend && terraform init && terraform apply`
It is crucial for the above to build with the correct backend URL when [building](#frontend-2)
* `cd ./infrastructure/backend && terraform init && terraform apply`
For the above you will be asked for the image selection - it should either be the SHA of the image e.g. `@sha256:12345` or `:actual-tag`

## CI

The current CI is based in GitHub and essentially does all the above:
* Always lint and test
* On the main branch, build and deploy
* Separate E2E test workflow dispatch

`Note`: all instructions for separate actions in this README should be present in the CI definitions in the `.github/workflows` folder, specifically the nested `main.yml` and `e2e.yml` files as a reference

## Extra functionality

The frontend includes a toggle that determines whether to use conversation history—either propagating the message history or sending only the initial prompt. While the application propagates the correct message sequence, the Anthropic API does not process it correctly and cannot answer follow-up questions about the transcript. This behavior is likely due to model limitations or token size constraints. For now, the toggle can be ignored, as it is intended for future extension

## Improvements currently out of scope

* Given the small number of documents, they are currently embedded directly into the backend Docker image. In a more extensive scenario, this approach would be replaced with a dedicated document database, such as MongoDB, to ensure scalability and efficient data management
* A distributed cache would replace the current local one, which is only a stub and disappears if the container crashes. This is acceptable for the current application, as it is scaled to a single replica (configurable in Terraform). However, for larger-scale deployments, a managed distributed cache like Redis would be a more appropriate solution, providing persistence and reliability
* An API gateway with authentication could be introduced for the backend service to provide enhanced DDoS protection and restrict unauthorized access
