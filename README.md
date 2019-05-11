# Blog Microservices

### How to start using Foreman 
#### foreman start --formation all-3

This will begin all the flask applications and set up the databases.

## NGINX 
Instal NGINX with its extras 
### $ sudo apt install --yes nginx-extras
Got to NGINX deafault file located in /etc/nginx/sites-enabled/default
Change the Default file with our file
Change ports if need to depending on your configuration

## Authentication
When you visit localhost it will ask you to login because of authentication.
The login that will work is:
username: email
password: password

### Also run:
#### pip3 install -r requirements.txt

This installs requirements for the app.

## How to run test scenarios in Tavern. 
Only thing we were able to get working is tags. And RSS on thunderbird


#### tavern-ci test_server.tavern.yaml

This will run the test scenarios within the .tavern.yaml


