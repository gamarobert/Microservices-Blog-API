# Blog Microservices

### How to start using Foreman 
#### foreman start --formation all-3

This will begin all the flask applications and set up the databases.

## NGINX 
Install NGINX with its extras 
### $ sudo apt install --yes nginx-extras
Got to NGINX deafault file located in /etc/nginx/sites-enabled/default
Change the Default file with our file
Change ports if need to depending on your configuration
### $ sudo service nginx restart

## Authentication
When you visit localhost it will ask you to login because of authentication.
The login that will work is:
username: email
password: password

### Also run:
#### pip3 install -r requirements.txt
This installs requirements for the app.

### Load Testing
#### siege -c25 -t1m http://localhost/rss/full
#### Project 2 W/O Caching
Unfortunately, Siege had an issue with our project 2 when testing with 25 concurrent users.
If this issue gets solved, we will update this readme file.

#### Project 3 W/ Caching
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


### Due to Siege breaking when using 25 concurrent users we tested with 1 concurrent user just to have something to compare
#### siege -c1 -t1m http://localhost/rss/full
#### Project 2 W/O Caching
** SIEGE 4.0.4  
** Preparing 1 concurrent users for battle.  
The server is now under siege...  
Lifting the server siege...  
Transactions:		                    7 hits  
Availability:		                  100.00 %  
Elapsed time:		                   59.70 secs  
Data transferred:	                 0.00 MB  
Response time:		                   8.04 secs  
Transaction rate:	                 0.12 trans/sec  
Throughput:		                      0.00 MB/sec  
Concurrency:		                     0.94  
Successful transactions:           7  
Failed transactions:	              0
Longest transaction:	              8.10  
Shortest transaction:	             7.96  

#### Project 3 W/ Caching
** SIEGE 4.0.4  
** Preparing 1 concurrent users for battle.  
The server is now under siege...  
Lifting the server siege...  
Transactions:		                  436 hits  
Availability:		               100.00 %  
Elapsed time:		                59.57 secs  
Data transferred:	              0.17 MB  
Response time:		                0.14 secs  
Transaction rate:	              7.32 trans/sec  
Throughput:		                   0.00 MB/sec  
Concurrency:		                  1.00  
Successful transactions:        436  
Failed transactions:	           0  
Longest transaction:	           1.16  
Shortest transaction:	          0.11  

### Even with out these tests, it is clear to see how much faster the requests are being made by looking at Foreman make requests while using the authorization headers instead of routing through /auth route.
