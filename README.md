# Djabber

#### Video Demo: https://www.youtube.com/watch?v=8oGuziC_vZY

#### Description: what and why

Djabber is a real time livechat/group chat web application, along the lines of WhatsApp or Facebook messenger. The desire to create an app like this came from my final project during the original CS50 course, for this project I created a social media clone called Pyspace and at the time I wanted to add more features that are common on most social medias, with instant messenger functionality being the principle one. 

However, due to the time constraints and the complexity of a project like this I feel like it wasn't feasible to add it to my previous project as it required more care and attention to create it to a good standard. Hence why I was enthusiastic to be able to do it as my final project for CS50 web, especially after what I have learned during the course has helped to develop this app successfully. 

The **frontend** again was made using HTML, CSS and Bootstrap and this time Javascript was used in conjunction with WebSockets for the dynamic parts of the client side, in particular the updating of messages being sent in real time to multiple users at once. The **backend** is based on the Django framework and Django channels to support the chat features. Rather than use an SQL database directly myself I've used the models feature of Django which I will go into more detail below. 

The name Djabber comes from the English word jabber, which means to talk quickly, enthusiastically and sometimes incoherently and the "Dj" associated with Django, with the "D" being silent. 

#### Distinctiveness and Complexity:

Of the projects that I completed during the course the closest would be Mail as both projects are based on mailing and messaging functionality. I believe my final project is sufficiently distinct from this because my application allows for instant messaging in real time with multiple users at once whereas the Mail project was one on one communication that had a delay when sending/receiving messages. 

While I did draw on lessons learned during completion of the Mail project I think more complexity was added as I have implemented technologies and frameworks that I was not familiar with and were not covered during CS50 web, for example Django Channels and Web Sockets. Therefore, a lot of my time creating this project was spent reading the documentation and researching how to implement this successfully along side a lot of trial and error and bug testing. While I'm sure more complex projects can be made for the final project I feel like the essence of a course like CS50 is having the confidence to go out and learn something new independently while creating a project and I believe I have done that rather than just staying within the confines of what was taught directly during the course.  

I think further complexity was added by the additional features such as the ability to create, edit (adding/removing members), deleting rooms and allowing users to leave rooms while updating messages sent in the frontend and saving them asynchronously to the backend database using the sync_to_async decorator. 

I also used multiple models to represent users, the chat rooms and any messages being saved to the database that link together. For example, the Room object has an owner which is the foreign key of the User object, there is also a ManyToMany connection that allows multiples users to be members in that room.

I had planned on deploying this project on AWS. I created a postgresql database on the cloud and configured it in my capstone settings.py file, however when I tried to migrate the database I kept getting and OperationalError saying that connection to the relevant server at the specified port had failed. 
I took several steps to fix this bug; I've checked my configuration several times and it is correct, I have internet access and the AWS RDS server is available, I've disabled my firewall that may have been blocking it, I've updated the RDS security groups to accept incoming connections on port 5432 and from my IP address, I've checked the network ACL and VPC settings which seem to be right to the best of my knowledge. I have also pinged the RDS endpoint which timed out and checked the RDS logs but they doesn't appear to have any errors.
The only solutions I'm yet to try is to try accessing the server from a different machine or by contacting AWS support but due to the deadline I'm afraid I'll not be able to include this in my final project as intended and is something I want to revisit at a later date. 

#### What’s contained in each file you created:

For the sake of brevity I'm going to assume that the reader is familiar with the Django framework and the inherit files such as styles.css, layout.html, admin.py, urls.py and manage.py. In the capstone python files some change have had to be made to accommodate WebSockets and wsgi. I'm also going to assume that login, logout, and register are self explanatory so I won't be covering them or the functions in views.py here. More information can be found in either the relevant documentation or the ReadMe.md of my CS50 final project available on Github (Wilson2453).

## Models

There are 3 models for this project;

**User** which inherits from Django's AbstractUser and can store information like username, password, email address, first/second names and superuser access.

**Room** this is used to store the information for each room/group that's created. Each room has an owner which is a foreign key of User and is determined by who creates the group, a name, and a slug which is whats used in the URL to direct users to the correct room. Finally, rooms can have a number of members, which is a many to many field with Users, this means that rooms can have multiple members and members can be a part of multiple rooms. 

**Message** stores the information for each message that is sent. Each message is linked to a room and a user (both foreign keys) and has a content which is the message that has been sent. Finally, the date-time is logged whenever the message has been saved, this allows us to display when the message was sent and then order the messages to get the most recent ones first, via the class Meta. 

## Consumers and routing

**Routing.py** has a single purpose which is to provide the path for our WebSockets to operate by passing the room_name via the url and then utilizes our ChatConsumer object which is defined in consumers.py. There is an argument that this could have been included in our urls.py file but I think it is more explicit for it to have its own file as when writing the code it is easier to recall that routing handles the websocket path and urls handles the web page paths. 

Our ChatConsumer object in **consumers.py** handles the WebSocket connections for the chat room. Firstly, it inherits from 'AsyncWebsocketConsumer' which is a base consumer class built into Django Channels for handling asynchronous WebSocket connections. 

The **connect method** takes the room_name from the url and creates a room_group_name based on it then adds the consumers to the chat room hence connecting them. 

The **disconnect method** is called when the Websocket connection is closed and removes the consumers channel from the chat room. 

The **receive method** parses the incoming JSON data which contains a message, username, and room, it then saves the message to the database using the save_message method, before broadcasting the message to everyone in the chat using the group_send method. 

The **chat_message method** is used to send a received message to the group. 

Finally the **save_message method** uses the sync_to_async decorator to asynchronously save a Message object to the database by updating the user, room and content. 

## Forms

I created this Django form to deal with the creating of a new room. However, I ran into an unknown bug and was unable to fix it in a reasonable amount of time. Therefore, I handled the form using HTML and then the logic for create_room in views.py. At present this file isn't being used as part of the project but I've left it in incase I have time to revisit it. 

## Index

Index is the home page of my webapp. If the user is not signed in then they are redirected to the login page. When the user signs in a list of all the groups they are a part of are listed here, a user would simply have to click the 'Join' button of the relevant room to access it. 

## Room

Room can be considered to the most important part of the project as it is where users can communicate with multiple other members at once. It extends layout.html and displays the room name. An edit button is available to the owner to access edit room and a leave group button is available for other users to leave the room as expanded on below. A chat box style container is the main visual aspect of this page and loops through the messages currently in this room from the database and displays the username, message, content and date-time of the message with a text box and submit button for adding new messages.

The main part of this file is the Javascript in the script tags, this sets up the WebSocket connection to the server via the constant variable chatSocket, this is printed to the console log along with .onopen and .onclose functions for testing purposes. 

Messages are received and displayed via chatSocket.onmessage this parses incoming JSON data, formats it with the sender's username and current date-time stamp, and updates the innerHTML of the chat window to show the message. 

Messages are sent via document.querySelector("#chat-message-submit").onclick. This is listening out for the event when the submit button is clicked and sends the user's message to the server. 

Finally, a scroll bar was added to the chat window by setting a limited height and the overflow-y value to auto. The scrollBottom function makes sure this window is scrolled so that the newest messages can be seen, this is called when the page first loads and after a new message is sent. 

## Create, edit and leave room

A logged in user can create a room by clicking it from the navbar, via the GET method this takes them to a page with a HTML form asking for the room name, specifies that they will be the owner, ask which users they want to add to the group and a button to submit the data. Once created the data is sent via the POST method to the backend and the room is created in the database, a slug is created from the room name provided and members are added using the save_member function. 

Edit room operates similarly but can only be accessed by the owner of a group, by clicking on the edit button in a room. This allows the owner to change the name of the room, add or remove members or even delete the room. The owner can't change the rooms slug or transfer ownership to anyone else. Upon confirmation the information is sent to the backend and updated in the database. 

Other members (non-owners) can leave a room by going into said room and clicking on the leave room button. Upon confirmation they will be deleted from the room in the database, however any previous messages will remain. 

## Error

Finally, there is a path for error handling. When the error function is called it takes a message as a parameter and displays the error page indicating what the error is and having a button to redirect to index. I thought it worth having this path due to the number of errors that can occur, it handles genuine errors such as a user trying to edit a room with a name already in use or trying to accessing a room that doesn't exist, or when adversaries try to take actions on a room via the URL such as trying to access, delete, edit or leave rooms in which they don't have authorization for.   

#### How to run your application/deployment 

Currently the application is only being run in a production/development environment and can be ran using the command "python manage.py runserver" command in the correct directory. I am planning on deploying this online via AWS and elastic beanstalk but that depends on time constraints. 
