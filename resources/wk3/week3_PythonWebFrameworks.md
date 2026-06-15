---
title: "Python Web Frameworks"
document_id: ""
version: "1"
date: "2025-07-02"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "0567cd3570bad657a04249d308702562cd9eaf4d0bcf47c1c99af4eebdda7857"
token_estimate: 1249
recommended_chunk_level: "h2"
abstract_for_rag: "The following frameworks abstract the low-level details so you can focus on your application logic (e.g. your ML model):"
source_file: "week3_PythonWebFrameworks.pdf"
type: "pdf"
extracted_via: "docling"
pages: 20
---

# Python Web Frameworks

## Overview

The following frameworks abstract the low-level details so you can focus on your application logic (e.g. your ML model):

- Flask:
- Lightweight 'micro -framework' for web dev
- Simple and minimalistic
- FastAPI (Our Focus):
- Modern, high-performance framework for building APIs
- Designed for speed and developer friendliness
- Comparatively new but popular for building RESTful APIs

## 5 minute Break

8 questions

## FastAPI Introduction

## Intro -Key Features and Advantages

- High Performance: Fastest Python framework - can handle many requests with low latency
- Developer Friendly: Easy and intuitive
- Fast to Code: Offers simplicity, editor auto-completion → increases development speed
- Automatic Documentation: Auto-generates interactive API docs
- Validation and Error Handling: Input data is validated automatically

## FastAPI Essentials: From Zero to API

Create and activate a virtual environment

```
Installation → pip install fastapi uvicorn
```

Uvicorn is an ASGI server (ASGI is the interface FastAPI uses to run)

In a file (main.py), you can spin up a FastAPI app:

```
from fastapi import FastAPI
```

```
app = FastAPI()
```

This app object will be our web application - creates an instance of FastAPI

## FastAPI Essentials: From Zero to API

Define a Route (Endpoint): Use Python decorators on functions to define API endpoints:

```
@app.get("/") def read_root(): return {"Hello": "World"}
```

This creates a GET endpoint at path '/' (the root URL).

When a client requests this URL, the function runs and returns a Python dict.

## FastAPI Essentials: From Zero to API

Running the Server: Launch with Uvicorn. For development, you can run:

```
uvicorn main:app --reload
```

This starts the server at http://127.0.0.1:8000

Now GET / on that address returns Hello World JSON.

```
from fastapi import FastAPI app = FastAPI(title="My ML API", version="1.0.0") @app.get("/") def read_root(): return{"message": "Hello World"} @app.get("/health") def health_check(): return {"status": "healthy"}
```

## Handling Inputs

- Path
- Query
- Body

## Path parameters

Enables us to capture parts of the URL as parameters

```
@app.get("/items/{item_id}") def read_item(item_id): return {"item_id": item_id}
```

Value of the path parameter: item\_id → passed to function as argument item\_id

Go to → http://127.0.0.1:8000/items/snowboard

Response → {"item\_id ": 'snowboard'}

You can declare the type of a path parameter in the function, using standard Python type annotations

```
@app.get("/items/{item_id}") def read_item(item_id: int): return {"item_id": item_id}
```

FastAPI's validation ensures item\_id is an integer (it will return a clear error if a non-int like "abc" is used)

## Query Parameters

Additional info is provided after a ? in the URL

/items/42?q=hello - those are query parameters

FastAPI injects them if your function signature has matching names

```
@app.get("/items/{item_id}") def read_item(item_id: int, q: str = None): return {"item_id": item_id}
```

A request to /items/42?q=hello would return:

```
{"item_id": 42, "q": "hello"}
```

## Path & Query Parameters

## · Data Validation:

- Type hints (item\_id: int) - FastAPI will automatically respond with an error

## · Combining Path and Query:

- In ML context, might use path params for identifying a model or version
- Query params could be used for optional settings (like a confidence threshold)

## · Both offer:

- Editor support
- Data "parsing' and Data validation
- Automatic documentation

## Body

- For sending complex data
- A request body is data sent by the client to your API.
- A response body is the data your API sends to the client.
- Your API almost always must send a response body - But clients don't necessarily need to send request bodies all the time.
- Request is used for POST or PUT
- Clients often send a JSON body (for example, a set of features for prediction).
- FastAPI makes it easy to accept and validate request bodies via Pydantic models .

## Pydantic Models

Pydantic is a Python library to perform data validation.

You declare the "shape" of the data as classes with attributes.

FastAPI is all based on Pydantic.

```
from pydantic import BaseModel class Item(BaseModel): name: str price: float tax: float | None = None
```

## Declare it as a Parameter

```
@app.post("/items/")
```

```
def create_item(item: Item): return item
```

## Request body + path + query parameters

```
@app.put("/items/{item_id}") def update_item(item_id: int, item: Item, q: str | None = None): result = { ' item_id": item_id, **item.dict()} if q: result.update({ 'q' :q} return result
```

## Concurrency and async/await

If you are using third party libraries that tell you to call them with await, like:

```
results = await some_library()
```

Then, declare your path operation functions with async def like:

```
@app.get ('/') async def read_results(): results = await some_library() return results
```
