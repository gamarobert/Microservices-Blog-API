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


student@tuffix-vm:~/Desktop/FinalProj/CPSC476-Project3$ siege -t1m -c25 localhost/rss/full
** SIEGE 4.0.4
** Preparing 25 concurrent users for battle.
The server is now under siege...
Lifting the server siege...
Transactions:                    579 hits
Availability:                 100.00 %
Elapsed time:                  59.49 secs
Data transferred:               0.23 MB
Response time:                  1.82 secs
Transaction rate:               9.73 trans/sec
Throughput:                     0.00 MB/sec
Concurrency:                   17.69
Successful transactions:         579
Failed transactions:               0
Longest transaction:           54.45
Shortest transaction:           0.00
 


