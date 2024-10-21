# PDF Q&A Assistant using AI

This project is an AI-powered assistant that extracts answers from large PDF documents and sends the results to a Slack channel using OpenAI’s GPT-3.5-turbo model. The assistant leverages ChromaDB to store and query embeddings, enabling efficient information retrieval from large documents.

## Features
- Extracts information from PDF files and answers questions based on the content.
- Integrates with Slack to send responses to a designated channel.
- Utilizes ChromaDB as the vector store for embedding text chunks.
- Powered by the MiniLM-L6-V2 model (using ONNX runtime) for fast and efficient embedding generation.

## Tech Stack
- **ChromaDB**: Vector database for storing text embeddings.
- **OpenAI GPT-3.5-turbo-0125**: Language model for processing user queries.
- **Slack API**: For sending query results to Slack.

## Project Structure
The project is organized into four key Python files:
1. **utils.py**: Manages PDF processing, embedding, and querying.
2. **app.py**: Makes the API router for user interfacing.
3. **req.txt**: Lists the required dependencies for the project.

### Environment Setup
Ensure you have the OpenAI API key and Slack App Authentication Token available in your environment to enable interaction with the OpenAI model and Slack workspace.

## Workflow
1. **User Input**: The user provides the file path of a PDF and a list of questions. Additional parameters include options to clear the vector store, define chunk sizes, and specify the number of query results to return.
2. **Text Chunking**: The assistant extracts text from the PDF and breaks it into chunks based on a user-defined word limit. Each chunk is stored as a complete sentence, even if the word limit is exceeded.
3. **Storing Embeddings**: The extracted text chunks are stored in ChromaDB as embeddings. Each chunk is tagged with metadata, such as the page number it came from.
4. **Query Processing**: When the user submits a question, the system queries the ChromaDB to retrieve relevant text chunks.
5. **Answer Generation**: The retrieved text chunks and user queries are passed to the GPT-3.5 model to generate an answer.
6. **Slack Integration**: The answer is formatted as a JSON object and sent to a specified Slack channel via the Slack App.

## Usage

1. **Install dependencies**:
   Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```

2. **Run the assistant**:
   Use the Swagger or HTTP API to provide a PDF file and a list of queries:
   ```
   python app.py
   ```
   This will start the server at 8000 port.

   Example call: 
   ```
    curl -X 'POST' \
    'http://localhost:8000/get-anwers?n_results=1' \
    -H 'accept: application/json' \
    -H 'Content-Type: multipart/form-data' \
    -F 'questions=Who is the CEO of the company?' \
    -F 'pdf_file=@handbook.pdf;type=application/pdf'
   ```

3. **Slack Setup**:
   Ensure that the Slack App is created and has access to the relevant channel in your workspace. Set up the Slack App Auth Token in your environment.

## Enhancements

Future improvements could include:
- A Streamlit-based graphical interface for easier interaction.
- Support for processing multiple PDFs at once for improved retrieval.
- Integration of context-based retrieval methods (e.g., RAG) for more accurate responses.
- Switching to more powerful vector databases like OpenSearch for larger-scale applications.
