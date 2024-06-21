The code you can find in this folder shows my resolution for proposed exercise.

'Exploratory notebook.ipynb' is jupyther notebook in which I ran all my tests and where a primitive version of my code can be found.

The results from said notebook are store in .json format in the '\respuestas' folder.

'app.py' is the REST API and my resolution for the exercise. In order to run it, I have done the following:

1. run anaconda
2. cd route_of_app.py
3. python app.py
4. Then I used postman to send a POST request of example 1 with the following command:
curl -X POST -H "Content-Type: application/json" -d 'FULL_EXAMPLE_1_DICTIONARY_HERE' http://localhost:5000/productionplan

The comments are in spanish, although I could provide a translation with no problem at all.