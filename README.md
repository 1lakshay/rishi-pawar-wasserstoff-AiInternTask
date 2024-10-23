# Internship Task: Domain-Specific PDF Summarization & Keyword Extraction Pipeline 

## Overview - 
This project implements the PDF summarization and keyword generation pipeline for multiple Pdf's, adopting the concurrency and the updation of these data into MongoDB. 

## Folder Structure - 
- README.md: This file.
- Dockerfile: to create image for efficient deployment and handling all the code and packages.
- main.py: The main python code file.
- requirements.txt: contain all the modules required to run this application.
- compressed_wasserstoff_vid: video describing the approach to a problem.

## workflow:

### Dockerfile - 
Dockerfile is used for the management of all the libraries and modules by creating a self-contained isolated space.
This makes the deployment process easy by uploading this file to GitHub and then deploying it using the railway.app
The railway identifies the docker file automatically and deploys it for you.

### Requirements.txt - 
in this file, all the libraries and modules are typed so that this can be loaded via the docker file to the container and can be executed inside 
It is used to install all the packages inside it.

### model of GPT-3.5 turbo is used via API key - 
An API key is used which has certain call limits.

### Extraction of text from pdf's - 
The text from the pdf's are extracted with the help of PyPDF2 

### Finding of domains - 
The domains that are most relevant to the particular pdf's text are found with the help of the model.
because they will help us find the keywords that have the same context as the domains.

## preprocessing of text for summarization - 
The text is split into sentences which can collectively be sent to the model for the summarization task. 
For this, there is a need to take care of the constraint of token limit for the model.
LOGIC:
![image](https://github.com/user-attachments/assets/0e99ff41-0df7-4dce-9a24-e370d5f2f952)

In the code snippet below.
The slicing technique is used to pass only the selected pair of sentences which satisfies the constraint. 
Var - count is used to check for the token limit and later then also used as a flag to append even the last pair of sentences after the while loop is executed.
![image](https://github.com/user-attachments/assets/519f3b74-885e-4fcd-9f62-16c3d2502d5a)


### The text is split into the words - 
The stopwords are loaded from the nltk library in which more words like: ["are", "a", "an", "shall", "may","also", "under","within","every","any","all"] are updated because they don't help us in any way to find the keywords.
Then the common words from the words that are also present in the stopwords are removed. Then all the words are passed to the Model along with the DOmains that we extracted.
By joining them because in this way the token limit for the model is to be satisfied always and reduce the latency time also text is split into the Sentences -
the text is splitted into the sentence by using the .splut("."). As till help us to generate the summary.
If the token limit starts to get more then that number of sentences arisnly passed to the model.

