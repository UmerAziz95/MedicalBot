to run the bot: python -m web.app
to create the rag: python load_documents.py (it goes to static/documents/) and load dynamically each file and store it into the rag

The vector store now relies on PostgreSQL with the pgvector extension. Configure the
database connection via the `PGVECTOR_CONNECTION_URI` environment variable (default:
`postgresql://postgres:postgres@localhost:5432/medicalbot`) and ensure the pgvector
extension is installed in your PostgreSQL instance before loading documents.