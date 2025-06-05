#!/bin/bash
#create necessary html page and prep index html file
current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";

printf  "Hello World \n
         Hostname: <font color='red'> $HOSTNAME </font> \n \
         Configured Value: <font color='blue'> $CONFIGURABLE_VALUE </font> $current_date_time \n " \
        > /usr/local/apache2/htdocs/index.html

#start the httpd service
/usr/local/apache2/bin/httpd -DFOREGROUND