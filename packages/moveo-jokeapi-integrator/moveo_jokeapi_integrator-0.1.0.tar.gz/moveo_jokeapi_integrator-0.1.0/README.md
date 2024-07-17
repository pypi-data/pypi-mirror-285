[![Unit Tests](https://github.com/JoneSabino/moveo-tech-challenge/actions/workflows/run-tests.yml/badge.svg)](https://github.com/JoneSabino/moveo-tech-challenge/actions/workflows/run-tests.yml)
[![Ruff Linting](https://github.com/JoneSabino/moveo-tech-challenge/actions/workflows/run-lint.yml/badge.svg)](https://github.com/JoneSabino/moveo-tech-challenge/actions/workflows/run-lint.yml)
![Vercel Deploy](https://deploy-badge.vercel.app/vercel/moveo-tech-challenge?style=plastic&name=Vercel)

# Moveo Tech Challenge

## Project Overview
This project is a tech challenge repository designed to showcase skills and solutions for Moveo.ai integration. The repository contains the necessary code and documentation to demonstrate the implementation of a webhook system and related functionalities.

## Features
- **Webhook Integration**: Implementing a webhook system with Moveo.ai.
- **Python Backend**: Server-side logic using Python.
- **Testing**: Includes test cases to ensure code reliability.

## Getting Started

### Prerequisites
- Python 3.12 or higher
- [PDM](https://pdm.fming.dev/latest/)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/JoneSabino/moveo-tech-challenge.git
    ```
2. Navigate to the project directory:
    ```bash
    cd moveo-tech-challenge
    ```
3. Install dependencies using PDM:
    ```bash
    pdm install
    ```

### Running the Server
To start the server, run:
```bash
python server.py
```

### Testing
Run tests using:
```bash
pytest
```

## Project Structure

- **src/**: Contains the main source code.
- **tests/**: Contains test cases.
- **.github/workflows/**: GitHub Actions for CI/CD.
- **server.py**: Main server file.
- **requirements.txt**: Python dependencies.
- **vercel.json**: Configuration for deployment on Vercel.
