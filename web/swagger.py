"""
Lightweight OpenAPI specification and Swagger UI template for the Medical Bot API.
"""
from config.settings import MAX_RETRIEVED_CHUNKS

SWAGGER_UI_TEMPLATE = """<!doctype html>
<html>
<head>
  <title>Medical Bot API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({
        url: "{{ spec_url }}",
        dom_id: '#swagger-ui',
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
      });
    };
  </script>
</body>
</html>"""


def get_openapi_spec():
    """Return an OpenAPI 3.0 specification dictionary for the Medical Bot API."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Medical Bot API",
            "version": "1.0.0",
            "description": (
                "Endpoints for querying the Medical Bot RAG system. "
                "The API injects a medical disclaimer, retrieved RAG context, and prior "
                "chat history into the LLM prompt so responses stay scoped to medical topics."
            ),
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Local development server",
            }
        ],
        "paths": {
            "/api/v2/medical-query": {
                "post": {
                    "summary": "Submit a medical question",
                    "description": (
                        "Runs the Medical Bot pipeline with disclaimer text, retrieved RAG "
                        "chunks, and optional prior conversation context."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "example": "What are early symptoms of hypertension?",
                                        },
                                        "tenant_id": {
                                            "type": "string",
                                            "example": "tenant_5dsolutions",
                                        },
                                        "workspace_id": {
                                            "type": "string",
                                            "example": "ws_marketing_ops",
                                        },
                                        "include_history": {
                                            "type": "boolean",
                                            "default": True,
                                        },
                                        "session_id": {
                                            "type": "string",
                                        },
                                        "k": {
                                            "type": "integer",
                                            "default": MAX_RETRIEVED_CHUNKS,
                                            "minimum": 1,
                                        },
                                        "disclaimer": {
                                            "type": "string",
                                            "example": "Responses are informational and not a substitute for professional care.",
                                        },
                                        "prior_chat_history": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "role": {"type": "string"},
                                                    "content": {"type": "string"},
                                                },
                                            },
                                        },
                                        "external_knowledge_instructions": {
                                            "type": "string",
                                            "example": (
                                                "You are a medical education assistant. "
                                                "Maintain continuity with prior chat history."
                                            ),
                                        },
                                    },
                                    "required": ["query"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Successful medical response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "answer": {"type": "string"},
                                            "classification": {"type": "string"},
                                            "disclaimer": {"type": "string"},
                                            "chunks_found": {"type": "integer"},
                                            "session_id": {"type": "string"},
                                            "conversation_history_included": {"type": "boolean"},
                                            "context_snippets": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "content": {"type": "string"},
                                                        "metadata": {
                                                            "type": "object",
                                                            "additionalProperties": True,
                                                        },
                                                        "similarity": {
                                                            "type": "number",
                                                            "format": "float",
                                                        },
                                                    },
                                                },
                                            },
                                            "tenant_id": {"type": "string"},
                                            "workspace_id": {"type": "string"},
                                            "rag_context": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "400": {
                            "description": "Invalid request payload",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            },
                        },
                        "500": {
                            "description": "Server error",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            },
                        },
                    },
                }
            },
            "/api/status": {
                "get": {
                    "summary": "Get system status",
                    "responses": {
                        "200": {
                            "description": "Status details",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            },
                        }
                    },
                }
            },
            "/api/openapi.json": {
                "get": {
                    "summary": "Fetch OpenAPI spec",
                    "responses": {
                        "200": {
                            "description": "OpenAPI specification",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            },
                        }
                    },
                }
            },
        },
    }
