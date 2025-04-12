# AgentSphere

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg)](https://docs.djangoproject.com/en/5.0/releases/5.0/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A dynamic AI platform enabling users to interact with agents individually or in groups, create workflows, and integrate MCP tools for seamless task automation.**

## 🌟 Features

- **🤖 AI Agents**: Create and manage AI agents with customizable system prompts
- **🔄 LLM Integration**: Connect to various LLM providers (Ollama, Gemini)
- **🏢 Organizations**: Create and manage organizations with multiple members
- **🔧 MCP Tools**: Integrate external tools via MCP servers
- **👥 Multi-User**: Collaborative environment with user management
- **🔒 Secure**: API keys stored securely in HashiCorp Vault
- **📊 API Documentation**: Comprehensive API documentation with Swagger/ReDoc
- **🚀 Scalable**: Built with Docker for easy deployment and scaling

## 🛠️ Tech Stack

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL
- **Cache & Message Broker**: Redis
- **Task Queue**: Celery
- **Secret Management**: HashiCorp Vault
- **Storage**: MinIO (S3-compatible)
- **Containerization**: Docker, Docker Compose
- **Documentation**: drf-spectacular (OpenAPI)
- **Monitoring**: Sentry, Django Silk
- **Email**: Mailpit (development)

## 📋 Prerequisites

- Docker and Docker Compose
- Git

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/yourusername/agentsphere.git
cd agentsphere
```

### Environment Setup

1. Copy the example environment files:

```bash
cp .envs/.django.env.example .envs/.django.env
cp .envs/.postgres.env.example .envs/.postgres.env
cp .envs/.minio.env.example .envs/.minio.env
cp .envs/.vault.env.example .envs/.vault.env
cp .envs/.pgadmin.env.example .envs/.pgadmin.env
```

1. Update the environment files with your settings

### Start the Application

```bash
make up
```

This will start all services defined in the docker-compose.yml file.

### Access the Application

- **Django Admin**: [http://localhost:8080/admin/](http://localhost:8080/admin/)
- **API Documentation**:
  - Swagger UI: [http://localhost:8080/api/v1/swagger/ui/](http://localhost:8080/api/v1/swagger/ui/)
  - ReDoc: [http://localhost:8080/api/v1/swagger/redoc/](http://localhost:8080/api/v1/swagger/redoc/)
- **PgAdmin**: [http://localhost:8080/pgadmin/](http://localhost:8080/pgadmin/)
- **Mailpit**: [http://localhost:8080/mailpit/](http://localhost:8080/mailpit/)
- **Vault UI**: [http://localhost:8080/vault/ui/](http://localhost:8080/vault/ui/)
- **Flower (Celery monitoring)**: [http://localhost:8080/flower/](http://localhost:8080/flower/)

## 🧰 Development Commands

AgentSphere comes with a colorful Makefile that provides convenient commands for development:

```bash
make help              # 🔍 Show help message
make up                # 🚀 Start all containers
make down              # 🛑 Stop all containers
make infra-up          # 🏗️ Start infrastructure services only
make app-up            # 📱 Start application services only
make ps                # 📋 List running containers
make logs              # 📜 View logs from all containers
```

## 🏗️ Project Structure

```text
agentsphere/
├── apps/                  # Django applications
│   ├── agents/            # AI agents functionality
│   ├── common/            # Shared utilities and models
│   ├── organization/      # Organization management
│   ├── tools/             # MCP tools integration
│   └── users/             # User management
├── compose/               # Docker compose configuration
├── config/                # Django settings and configuration
├── docs/                  # Documentation
└── requirements/          # Python dependencies
```

## 🔑 Key Concepts

### Agents

AI agents are the core of AgentSphere. Each agent has:

- A name and description
- A system prompt that defines its behavior
- A connection to an LLM for generating responses
- An automatically generated avatar

### LLMs

Language Model configurations that can be connected to agents:

- Support for multiple API providers (Ollama, Gemini)
- Secure API key storage in HashiCorp Vault
- Configurable token limits

### Organizations

Organizations provide a way to group users and resources:

- Each user can create up to 3 organizations
- Organizations can have up to 8 members
- Resources (Agents, LLMs, MCP tools) are associated with organizations

### MCP Tools

MCP (Multi-Agent Communication Protocol) tools allow integration with external services:

- Each user can add up to 5 MCP tools per organization
- Tools are defined by name, description, URL, and optional tags

## 📚 API Documentation

The API is documented using OpenAPI 3.0 (via drf-spectacular). You can explore the API using:

- **Swagger UI**: [http://localhost:8080/api/v1/swagger/ui/](http://localhost:8080/api/v1/swagger/ui/)
- **ReDoc**: [http://localhost:8080/api/v1/swagger/redoc/](http://localhost:8080/api/v1/swagger/redoc/)

## 🔒 Security

- User authentication via JWT tokens
- API keys stored securely in HashiCorp Vault
- CSRF protection
- Secure cookie settings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Contact

Your Name - [rohit.vilas.ingole@gmail.com](mailto:rohit.vilas.ingole@gmail.com)

Project Link: [https://github.com/DataRohit/AgentSphere](https://github.com/DataRohit/AgentSphere)
