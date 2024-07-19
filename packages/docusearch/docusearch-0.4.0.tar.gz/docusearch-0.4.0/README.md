# Docusearch

Welcome to **Docusearch**, the ultimate tool for document searching and processing using the power of vector embeddings. Follow the steps below to get started quickly!

## Installation

First, you need to install the `docusearch` package using `pip`. Installation may take a minute or two. To avoid conflicts, it is recommend you use a virtual environment:

```sh
pip install docusearch
```

## Usage

### Step 1: Import the Module
After installing the package, import the `process_query` function from the `docusearch` module:

```sh
from docusearch import process_query
```

### Step 2: Set the Parameters
Define the parameters for your query. You need to set your OpenAI API key, the path to the folder containing the documents, and the query for those documents

```sh
query = "What are some cool features of the Audi r8"
api_key = "your-openai-key"
folder_path = "path-to-your-folder"
```

### Step 3: Call the Function and Print the Result
Now, call the `process_query` function with the parameters you set and print the result:

```sh
result = process_query(query, api_key, folder_path)
print(result)
```

## Example

Here is the complete example code:

```sh
from docusearch import process_query

query = "What are some cool features of the Audi r8"
api_key = "your-openai-key"
folder_path = "path-to-your-folder"

result = process_query(query, api_key, folder_path)
print(result)
```

And that's it! You have successfully used the docusearch package to process your query. Enjoy searching your documents with ease!

## Additional Info

If you would like specific information about the result, you can use the `extract_info` function. It will provide you the document source, answer, citations, and warnings for unsupported files.

### Import the extract_info Function
```sh
from docusearch import extract_info
```

### Use the extract_info function to extract the document source, answer, citations, and any warnings:

```sh
document_source, answer, citations, warning = extract_info(result)

print(f"Document Source: {document_source}")
print(f"Answer: {answer}")
print(f"Citations: {citations}")
if warning:
    print(f"Warning: {warning}")
```

### Complete Example
Here is the complete example code to query and extract specific information:

```sh
from docusearch import process_query, extract_info

query = "What are some cool features of the Audi r8"
api_key = "your-openai-key"
folder_path = "path-to-your-folder"

# Process the query
result = process_query(query, api_key, folder_path)

# Extract information from the result
document_source, answer, citations, warning = extract_info(result)

# Print the extracted information
print(f"Document Source: {document_source}")
print(f"Answer: {answer}")
print(f"Citations: {citations}")
if warning:
    print(f"Warning: {warning}")
```

By following these steps, you can easily extract and use specific pieces of information from the result provided by the `docusearch` package. Have fun!