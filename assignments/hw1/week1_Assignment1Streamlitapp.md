---
title: "Assignment 1 - Streamlit app"
document_id: ""
version: "1"
date: "2026-06-15"
status: "draft"
document_type: ""
content_domain: []
authors: []
organization: ""
generation_metadata:
  authored_by: "unknown"
content_hash: "52e69e77ea787e3cf6c422ff0bba545263f5902a42494955d42911df1cf4d5c1"
token_estimate: 1281
recommended_chunk_level: "h2"
abstract_for_rag: "The goal of this assignment is to build a complete, end-to-end machine learning application. You will train a sentiment analysis model on movie review data, save it, and then build an interactive web app with Streamlit that allows a user to input any text and see the predicted sentiment. I have included sufficient hints and comments to assist you with completing this assignment easily."
source_file: "week1_Assignment1Streamlitapp.pdf"
type: "pdf"
extracted_via: "docling"
pages: 3
---

# Assignment 1 - Streamlit app

10 6/30/2026, 11:59:00 PM Points: Due:

## Homework Assignment : Building a Sentiment Analysis Web App with Streamlit

The goal of this assignment is to build a complete, end-to-end machine learning application. You will train a sentiment analysis model on movie review data, save it, and then build an interactive web app with Streamlit that allows a user to input any text and see the predicted sentiment. I have included sufficient hints and comments to assist you with completing this assignment easily. Feel free to email/Discord if you face any confusion. Objective:

Wednesday, 17th September. 11.59 pm MT Due Date:

## Part 1: Data Preparation and Model Training

In this part, you will prepare the data, train a Naive Bayes classifier, and save the trained model pipeline.

## Step 1: Get the Data

We will use the Large Movie Review Dataset (IMDB). For simplicity, you can use a pre-processed version available on Kaggle.

- Dataset: IMDB Dataset of 50K Movie Reviews
- Download the file from the link above and place it in your project folder. IMDB Dataset.csv

## Step 2: Create a Training Script

Create a Python script named train\_model.py. This script will be responsible for loading the data, training the model, and saving it.

## Step 3: Load and Preprocess the Data

## Step 4: Train the Model

For this task, a combination of TfidfVectorizer and MultinomialNB (Naive Bayes) is a strong and classic baseline. To make the model easy to use in, package them together in a Pipeline.

- Import from , from , and from . Pipeline sklearn.pipeline TfidfVectorizer sklearn.feature\_extraction.text MultinomialNB sklearn.naive\_bayes
- Create a pipeline that first transforms the text data using and then feeds it to the classifier. TfidfVectorizer MultinomialNB
- Train the pipeline on your entire dataset ( and ). No need to create a train-test split for this assignment X y

## Step 5: Save the Model Pipeline

- Once the model is trained, you need to save it to a file so your Streamlit app can use it later.
- Use the library to dump your trained object into a file named . Your script should only be run once to generate the file. joblib Pipeline sentiment\_model.pkl train\_model.py sentiment\_model.pkl

## Part 2: Building the Streamlit Application

Now for the fun part! You will create a web interface for your model.

Step 1: Create the App Script

Create a new Python script named app.py.

## Step 2: Set up the Basic App Layout

- Import and . streamlit joblib
- Give your application a title, for example: . Movie Review Sentiment Analyzer
- Write a short description of what the app does.

## Step 3: Load the Saved Model

```
· Write a function to load using . sentiment_model.pkl joblib.load()
```

- This ensures the model is loaded only once when the app starts, which is essential for performance. Crucially, use the decorator on this function (review Lab 1.5). @st.cache\_data

## Step 4: Create the User Input Interface

- Use to create a text box where the user can type or paste a movie review. Give it a descriptive label like "Enter a movie review to analyze:". st.text\_area()
- Add a button with labeled "Analyze". st.button()

## Step 5: Make Predictions and Display Results

- Write an block that checks if the "Analyze" button has been pressed. · Inside the block: 1. Get the text from the text area. 2. Make sure the user has entered some text before trying to make a prediction. 3. Use your loaded model pipeline's method on the user's text. Note that the pipeline expects a list or array of documents, so you'll need to pass the input text inside a list (e.g., ). 4. The output will be the predicted sentiment ( or ). 5. Display the result to the user in a clear way. Use or to show the prediction. Display the prediction probability using the model's method. 6. if if .predict() [user\_text] 'positive' 'negative' st.subheader() st.write() .predict\_proba()
- %æ Make the output more engaging! If the sentiment is positive, you could write "Predicted Sentiment: Positive Ø=ÜM " and if it's negative, "Predicted Sentiment: Negative Ø=ÜN ". Pro-tip:

## Step 6: Run Your App

Open your terminal in the project directory and run:

```
streamlit run app.py
```

Test your app with different reviews to see if it works as expected.

## Submission Guidelines

To receive full grade, you must push all the files on a GitHub repository (make sure it's public or add my email if you want to keep it private: ). rahimrasool17@gmail.com

You only have to add the GitHub URL when submitting the assignment. You can work in pairs; however, make sure to submit your work individually in separate accounts and repositories.

Ensure to include the following files:

1. (your model training script) train\_model.py
2. (your Streamlit application script) app.py
3. (the saved model file) sentiment\_model.pkl
4. A file listing the libraries needed to run your project (e.g., , , , ). requirements.txt streamlit pandas scikit-learn joblib
5. A README file with a simple paragraph on how to clone and run your app locally. Preferably, write it in bullet points.
