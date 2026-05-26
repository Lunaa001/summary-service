"""README - Summary Service Microservice"""

# Summary Service

Microservice for document summarization using AI (Gemma4 model).

## Features

- Generate document summaries using Gemma4 AI
- Store summaries in PostgreSQL database
- RESTful API for summary operations
- Quality checks for document text
- Full-featured logging and error handling

## Setup

### Requirements

- Python 3.12+
- PostgreSQL database
- Gemma4 API key

### Installation

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# or with pdm:
pdm install
```

3. Create `.env` file (see `.env.example`):
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=summary_service
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/summary_service
MODEL_API_KEY=your_api_key_here
MODEL_API_BASE_URL=https://ai.cloud.um.edu.ar/api/v1
IA_MODEL=gemma4-26b-16g
HOST=0.0.0.0
PORT=8002
LOG_LEVEL=INFO
```

4. Run database migrations:
```bash
# Tables will be created automatically on startup
```

## Running the Service

```bash
python main.py
# or with uvicorn:
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker Compose

```bash
docker compose up --build
```

Other services can reach this microservice at `http://app:8002` inside the Compose network.

## API Endpoints

### Health Check
- `GET /health` - Service health status
- `GET /` - API information

### Summary Operations

#### Generate Summary
- `POST /summaries/generate`
- Request body:
```json
{
  "documento_id": 1,
  "texto": "Document text to summarize...",
  "max_tokens": 300
}
```
- Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "documento_id": 1,
    "resumen": "Summary text...",
    "longitud_resumen": 150
  },
  "documento_id": 1,
  "message": "Summary generated successfully"
}
```

#### Get Summary by Document ID
- `GET /summaries/document/{documento_id}`
- Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "documento_id": 1,
    "resumen": "Summary text...",
    "longitud_resumen": 150,
    "fecha_creacion": "2024-05-11T10:30:00"
  },
  "documento_id": 1
}
```

#### Get Summary by ID
- `GET /summaries/{summary_id}`
- Response: Similar to above

## Database Schema

### resumenes (Summaries)
- `id` - Primary key
- `documento_id` - Reference to document
- `texto_original` - Original document text
- `resumen` - Generated summary
- `longitud_resumen` - Summary length in characters
- `tokens_utilizados` - Tokens used by AI model
- `modelo` - AI model used (gemma4-26b-16g)
- `fecha_creacion` - Creation timestamp
- `fecha_actualizacion` - Last update timestamp

## Project Structure

```
Summary-service/
├── app/
│   ├── controllers/      # API endpoint handlers
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── utils/           # Utilities and exceptions
│   └── database.py      # Database configuration
├── tests/               # Test files
├── config.py            # Configuration settings
├── main.py             # FastAPI application entry point
└── pyproject.toml      # Project dependencies
```

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Running Tests with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Error Handling

The service implements proper HTTP status codes and error responses:
- `200 OK` - Successful operation
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

All error responses include structured JSON with `success`, `message`, and `detail` fields.

## Logging

Logs are configured based on the `LOG_LEVEL` environment variable. Default is `INFO`.

## Performance Considerations

- Database connection pooling enabled (10 connections, max overflow 20)
- API timeouts set to 30 seconds for AI service
- Text length validation to avoid processing too-short documents
- Efficient database queries with proper indexing

## Future Enhancements

- [ ] Summary regeneration/updates
- [ ] Batch summary generation
- [ ] Summary quality metrics
- [ ] Caching layer for frequent summaries
- [ ] Support for multiple AI models
- [ ] Document language detection
- [ ] Summary in different languages

## License

MIT License

## Support

For issues or questions, contact the development team.
