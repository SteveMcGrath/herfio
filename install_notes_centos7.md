Add this repo to /etc/yum.repos.d:

````
[mongodb]
name=MongoDB Repository
baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/
gpgcheck=0
enabled=1
````

yum -y update 
yum -y install mongodb-org mongodb-org-server
systemctl enable mongod 
systemctl start mongod 
