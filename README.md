# This is task submission 

## workflow:

### Dockerfile - 
Dockerfile is used for the management of all the libraraies and modules by creating a self contained isolated space.
This makes the pdeployment process easy by uploading this file to the github and then deploying it using the railway.app
The railway identifies the dockerfile automatically and deploy it for you.

### Requirements.txt - 
in this file all the libraries and modules are typed so that this can be loaded via dockerfile to to the container and can be executed inside 
it to ibstall all the packages inside it.

### model of gpt-3.5 turbo is used via api key - 
Api key is used which have the certaiil call limits.

### Extraction of text form pdf's - 
The text from the pdf's are extracted with the help of PyPDF2 

### Finding of domains - 
the domains are find out with the help of the model whichc are most relevant to the particular pdf's text.
because they will help us in finding the keywords which have the same context as of the domains.

### The text is splitted into the words - 
The stopwords are loaded from the nltk libraray in which the nmore words like: ["are", "a", "an", "shall", "may","also", "under","within","every","any","all"] are updated because they don't help us in any way to find the keywords.
Then the common words form the words whichc are also present in the stopwords are removed. Then all the words are passed to the Model along with the DOmains that we extracted.
by joining them because in this way the token limit for model is to be satsfied always and reduce the latency time also for the application.

### The text is splitted into the Sentences -
the text is splitted into the sentence by using the .splut("."). as they will help us to generate the summary.
The logic of checking is made to check that whether these sentences while passing to the model dont exceeds the token limit of the model.
if the token limit starts to get more then that number of sentences are only passed to the model.

