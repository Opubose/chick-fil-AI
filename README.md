# Chick-fil-AI Chatbot

This project is an AI chatbot application for Chick-fil-A restaurants, developed as a senior design project (CS 4485) for Computer Science majors at The University of Texas at Dallas.
The following members contributed to this project:

1. Aditya Kulkarni
2. Agastya Bose
3. David Tepeneu
4. Dilon Sok
5. Grace Zhou

## Project Structure

The project is organized into two main subdirectories:

- `backend`: Contains the Flask API, NLP scripts, and database scripts
- `frontend`: Contains the React application

Both subdirectories have their own Dockerfiles for containerization.

## Prerequisites

Before running the application, ensure you have the following:

1. Docker and Docker Compose installed on your system
2. Required API keys and secrets:
   - Google Dialogflow key
   - Amazon AWS keys for DynamoDB
   - OpenRouter API key

## Getting Started

To run the application:

1. Clone this repository
2. Navigate to the project's root directory
3. Set up the required environment variables (see "Environment Variables" section below)
4. Run the following command:

```bash
docker compose up --build
```

This command will build and start both the backend and frontend containers.

## Environment Variables

Create a `.env` file in the project root directory with the following variables:

```
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_dialogflow_key
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

Replace the placeholder values with your actual API keys and secrets.

## Backend

The backend is built using Flask and serves as the API for the chatbot. It interacts with:

- Google Dialogflow for natural language processing
- Amazon DynamoDB to store and query the restaurant menu
- OpenRouter for cloud-based LLM response generation

## Frontend

The frontend is a React application that provides the user interface for interacting with the chatbot.

## Data Storage

The restaurant menu is stored in an Amazon DynamoDB table, which is queried by the backend during the runtime of the application.

## Contributing

This project is part of UTD's senior design course. No external contributions will be accepted.
