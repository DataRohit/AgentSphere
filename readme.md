# AgentSphere

<!-- Project Status -->
[![Project Status: Active](https://img.shields.io/badge/Project%20Status-Active-brightgreen)](https://github.com/DataRohit/AgentSphere)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/DataRohit/AgentSphere/blob/master/license)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/DataRohit/AgentSphere)

<!-- Core Technologies -->
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg?logo=django&logoColor=white)](https://docs.djangoproject.com/en/5.0/releases/5.0/)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-red.svg?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

<!-- Frontend Technologies -->
[![Next.js 15.3](https://img.shields.io/badge/Next.js-15.3-black.svg?logo=next.js&logoColor=white)](https://nextjs.org/)
[![React 19](https://img.shields.io/badge/React-19-blue.svg?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS 4](https://img.shields.io/badge/Tailwind-4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

<!-- Infrastructure -->
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-Stack-red.svg?logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-Task%20Queue-brightgreen.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Vault](https://img.shields.io/badge/HashiCorp-Vault-blue.svg?logo=vault&logoColor=white)](https://www.vaultproject.io/)
[![MinIO](https://img.shields.io/badge/MinIO-S3%20Storage-red.svg?logo=minio&logoColor=white)](https://min.io/)

<!-- Development Tools -->
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-green.svg?logo=openapi-initiative&logoColor=white)](https://www.openapis.org/)

**A dynamic AI platform enabling users to interact with agents individually or in groups, create workflows, and integrate MCP tools for seamless task automation.**

## 🌟 Features

### Backend Features

- **🤖 AI Agents**: Create and manage AI agents with customizable system prompts
- **🔄 LLM Integration**: Connect to various LLM providers (Only Gemini for Now!)
- **🏢 Organizations**: Create and manage organizations with multiple members
- **🔧 MCP Tools**: Integrate external tools via MCP servers
- **👥 Multi-User**: Collaborative environment with user management
- **🔒 Secure**: API keys stored securely in HashiCorp Vault
- **📊 API Documentation**: Comprehensive API documentation with Swagger/ReDoc
- **🚀 Scalable**: Built with Docker for easy deployment and scaling

### Frontend Features

- **🎨 Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS
- **🌓 Dark Mode**: Full support for light and dark themes
- **💬 Real-time Chat**: WebSocket-powered conversations with AI agents
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **🔐 Secure Authentication**: JWT-based authentication with secure cookie storage
- **⚡ Fast Performance**: Optimized for speed with Next.js App Router
- **🧩 Component Library**: Built with shadcn/ui and Radix UI primitives
- **🔄 State Management**: Centralized state management with Redux Toolkit

## 🛠️ Tech Stack

### Backend

- **Framework**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL
- **Cache & Message Broker**: Redis
- **Task Queue**: Celery
- **Secret Management**: HashiCorp Vault
- **Storage**: MinIO (S3-compatible)
- **Documentation**: drf-spectacular (OpenAPI)
- **Monitoring**: Sentry, Django Silk
- **Email**: Mailpit (development)

### Frontend

- **Framework**: Next.js 15.3, React 19, TypeScript 5
- **UI Components**: Tailwind CSS 4, shadcn/ui, Radix UI
- **State Management**: Redux Toolkit
- **Form Handling**: React Hook Form, Zod
- **Animations**: Framer Motion
- **HTTP Client**: Native fetch API
- **WebSockets**: Native WebSocket API

### Infrastructure

- **Containerization**: Docker, Docker Compose
- **Package Manager**: pnpm (frontend), pip (backend)

## 📋 Prerequisites

- Docker and Docker Compose
- Git

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/DataRohit/AgentSphere.git
cd AgentSphere
```

### Environment Setup

- Copy the example environment files:

```bash
cp .envs/.django.env.example .envs/.django.env
cp .envs/.postgres.env.example .envs/.postgres.env
cp .envs/.minio.env.example .envs/.minio.env
cp .envs/.vault.env.example .envs/.vault.env
cp .envs/.pgadmin.env.example .envs/.pgadmin.env
```

- Update the environment files with your settings

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

### Frontend Development Setup

For frontend development, you can run the Next.js development server separately:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies with pnpm
pnpm install

# Start the development server
pnpm dev
```

The frontend development server will be available at [http://localhost:3000](http://localhost:3000).

You can also use the Makefile command:

```bash
make nextjs-dev
```

## 🧰 Development Commands

AgentSphere comes with a colorful Makefile that provides convenient commands for development:

```bash
# Docker Commands
make help              # 🔍 Show help message
make up                # 🚀 Start all containers
make down              # 🛑 Stop all containers
make infra-up          # 🏗️ Start infrastructure services only
make app-up            # 📱 Start application services only
make ps                # 📋 List running containers
make logs              # 📜 View logs from all containers
make logs-app          # 📜 View logs from application containers
make logs-infra        # 📜 View logs from infrastructure containers
make build             # 🔨 Build all containers
make clean             # 🧹 Remove all containers, networks, and volumes
make restart           # 🔄 Restart all containers
make restart-app       # 🔄 Restart application containers
make restart-infra     # 🔄 Restart infrastructure containers

# Python Code Quality Commands
make lint              # 🔎 Run ruff linter on Python code
make format            # 💅 Format Python code with ruff
make fix               # 🔧 Fix auto-fixable issues with ruff

# Frontend Development Commands
make nextjs-dev        # 🚀 Start NextJS development server
make nextjs-build      # 🔨 Build NextJS application
```

## 🏗️ Project Structure

```text
AgentSphere/
├── .envs/                 # Environment variable files
├── backend/               # Django backend code
│   ├── apps/              # Django applications
│   │   ├── agents/        # AI agents functionality
│   │   ├── chats/         # Chat management (single & group)
│   │   ├── common/        # Shared utilities and models
│   │   ├── contrib/       # Contributed Django extensions
│   │   ├── conversation/  # Conversation sessions & websockets
│   │   ├── llms/          # LLM configurations & integrations
│   │   ├── organization/  # Organization management
│   │   ├── templates/     # Email and HTML templates
│   │   ├── tools/         # MCP tools integration
│   │   └── users/         # User management & authentication
│   ├── config/            # Django settings and configuration
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js frontend code
│   ├── app/               # App router pages and layouts
│   │   ├── auth/          # Authentication pages
│   │   ├── dashboard/     # Dashboard pages
│   │   ├── organizations/ # Organization management
│   │   ├── agents/        # Agent management
│   │   ├── chats/         # Chat interfaces
│   │   ├── group-chats/   # Group chat interfaces
│   │   ├── store/         # Redux store configuration
│   │   └── globals.css    # Global CSS styles
│   ├── components/        # Reusable React components
│   │   ├── ui/            # UI components (shadcn/ui)
│   │   └── ...            # Feature-specific components
│   ├── lib/               # Utility functions and helpers
│   ├── public/            # Static assets
│   └── package.json       # Frontend dependencies
├── compose/               # Docker compose configuration
│   ├── django/            # Django service configuration
│   ├── nginx/             # Nginx service configuration
│   ├── postgres/          # PostgreSQL service configuration
│   └── nextjs/            # Next.js service configuration
├── docker-compose.yml     # Docker compose services definition
└── makefile               # Development commands
```

## 🔑 Key Concepts

### Agents

AI agents are the core of AgentSphere. Each agent has:

- A name and description
- A system prompt that defines its behavior
- A connection to an LLM for generating responses
- An automatically generated avatar using DiceBear
- Public or private visibility within an organization
- A limit of 5 agents per user per organization

### LLMs

Language Model configurations that can be connected to agents:

- Support for multiple API providers (Currently Gemini 2.5 Pro/Flash)
- Secure API key storage in HashiCorp Vault
- Configurable token limits
- Organization-based access control

### Chats

AgentSphere supports two types of chat interactions:

- **Single Chats**: One-to-one conversations between a user and an agent
- **Group Chats**: Multi-agent conversations where a user can interact with multiple agents
- Both chat types support message history, editing, and deletion

### Conversation Sessions

Conversation sessions manage the flow of interactions:

- Link to either single or group chats
- Track active/inactive status
- Can use a selector prompt for routing to appropriate agents/tools
- Associate with specific LLM models for processing

### Organizations

Organizations provide a way to group users and resources:

- Each user can create up to 3 organizations
- Organizations can have up to 8 members
- Resources (Agents, LLMs, MCP tools) are associated with organizations
- Public/private visibility controls for resources

### MCP Tools

MCP (Multi-Agent Communication Protocol) tools allow integration with external services:

- Each user can add up to 5 MCP tools per organization
- Tools are defined by name, description, URL, and optional tags
- Secure authentication with external services

## 🏛️ Frontend Architecture

The frontend of AgentSphere is built with Next.js 15.3 using the App Router, providing a modern, type-safe, and performant user interface.

### Key Components

- **Authentication**: JWT-based authentication with secure cookie storage
- **State Management**: Redux Toolkit for global state management
- **UI Components**: Built with shadcn/ui, a collection of reusable components built on Radix UI
- **Real-time Communication**: WebSocket connections for live chat functionality
- **Form Handling**: React Hook Form with Zod schema validation
- **Animations**: Framer Motion for smooth transitions and interactions

### Page Structure

- **Landing Page**: Introduction to AgentSphere with feature showcase
- **Authentication**: Login, signup, account activation, and password reset
- **Dashboard**: Organization management and overview
- **Agent Studio**: Create and manage AI agents
- **Chat Interfaces**: Single and group chat conversations with agents
- **Organization Management**: Member management, settings, and permissions

### WebSocket Implementation

The chat functionality uses WebSockets for real-time communication:

- Secure authentication via JWT tokens
- Automatic reconnection handling
- Real-time typing indicators
- Support for both single-agent and multi-agent conversations

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

Rohit Ingole - [rohit.vilas.ingole@gmail.com](mailto:rohit.vilas.ingole@gmail.com)

Project Link: [https://github.com/DataRohit/AgentSphere](https://github.com/DataRohit/AgentSphere)

## 🔄 CI/CD Pipeline

AgentSphere uses a robust CI/CD pipeline to ensure code quality and automated deployments:

- **Linting**: Automated code quality checks using Ruff
- **Testing**: Automated tests run on each pull request
- **Docker**: Containerized builds for consistent deployment
- **Deployment**: Automated deployment to staging and production environments

## 📊 Project Status

AgentSphere is currently in active development. The core functionality is implemented, but we're continuously adding new features and improvements.

## 🌐 Supported LLM Providers

- **Gemini** (Currently supported)
- **OpenAI** (Coming soon)
- **Anthropic** (Coming soon)

## 💬 Getting Help

If you need help with AgentSphere, you can:

- **Open an Issue**: For bugs or feature requests
- **Discussions**: For general questions and discussions
- **Email**: Contact the maintainer directly at [rohit.vilas.ingole@gmail.com](mailto:rohit.vilas.ingole@gmail.com)

We welcome all feedback and contributions!
