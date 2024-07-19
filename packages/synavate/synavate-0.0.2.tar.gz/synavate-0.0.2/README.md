# Synavate Utilities 🌟

Synavate Utilities is a comprehensive package designed to streamline and enhance your data processing and analysis workflows. Packed with powerful tools and utilities, this package is essential for data scientists, engineers, and developers who work with complex data sets and need efficient solutions for their tasks. 📊🔧

## Key Features

### Data Generation & Testing 🧪

- **generate-tests**: Automatically generate test cases and manage test outputs with ease. This includes utilities for creating test data, managing configurations, and tracking utilities.

### Documentation & CI/CD 📄

- **autodoc_generator**: Generate documentation automatically for your projects.
- **cicd**: Configuration files and scripts for setting up continuous integration and continuous deployment pipelines using tools like CircleCI and Google Cloud Platform.

### Data Handling & Storage 📦

- **db**: Utilities for interacting with various databases including MongoDB, Redis, and Chroma. Provides scripts and modules for data loading, querying, and storage.
- **py**: Python modules for formatting, decorators, and GCP interaction.

### Docker & DevOps 🐳

- **docker**: Dockerfiles and scripts for containerizing applications, including a specific Dockerfile for Streamlit applications.
- **scripts**: Zsh scripts for managing folders and other utilities.

### Logging & Monitoring 📈

- **logs**: Tools for setting up and managing logging configurations, including integration with filebeat for log collection and monitoring.

## Getting Started

### Installation

You can install Synavate Utilities via pip:

```bash
pip install synutils
```

### Usage

Import the necessary modules from Synavate Utilities in your Python project:

```python
from synutils import main
```

### Example

Here's a quick example of how to use one of the utilities:

```python
from synutils.main import some_utility_function

# Use the utility function for your task
some_utility_function()
```
