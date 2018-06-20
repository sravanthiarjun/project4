# project4
# Item_catalog
### This project is the Fourth project of Udacity Full Stack Nanodegree course

### About project
  This project is completely based on developing an application with usage of framework known as Flask environment
  OAuth2 provides authentication for further CRUD functionality on the application. 
  Currently OAuth2 is implemented for Google Accounts.
#### Required:
      HTML
      CSS
      Python
      vagarnt
      virtualbox
      Flask Framework
      OAuth
#### In this respoiratory consists of folders:
    - templates:- consists of all html pages that is needed for the project
    -static:- consists of css file which is used for styling of my webpage
    
#### database_setup.py
    used for creating database that we required for the CRUD operations and classes we used
#### project.py
###### This is the main file which we are having every paths that are needed to perform our CRUD operations.
###### In this file we import all neccessary files that required for our project.

#### logmenuitems
###### consists of all data that is stored in database.

#### Google Login:
###### For API client ID:
###### we generate the client ID for the project by using Google Dev Console
        After generating API client ID for project then use that ID in login.html file
        Then after download the JSON file and use that file in our project.py file.
##### To Run:
###### After installing all requirments:
###### Goto vagrant folder make commands like vagrant up and vagrant ssh and goto vagrant folder.
###### Then after open flask-applcation folder and activate flask environment by using command:
        source flask-env/bin/activate
        To deactivate: just type deactivate
###### Then after run the python file to get our application.
###### Then open web browser and run localhost. 
##### Resources used:
###### udacity classroom videos in our course for this project.
###### Finally the code is checked under pep8 online checker
