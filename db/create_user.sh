#!/bin/bash
query2=GRANT ALL PRIVILEGES ON Jhin.* TO 'test'@'localhost' IDENTIFIED BY 'test';
mysql -e $query2;
mysql -e flush privileges