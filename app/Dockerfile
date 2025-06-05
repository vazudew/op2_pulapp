## get latest httpd image 
FROM httpd:2.4

ARG CONFIGURABLE_VALUE
ENV CONFIGURABLE_VALUE=${CONFIGURABLE_VALUE}
#prepare a script to create html page based on env variable
# also start httpd service
COPY create_html.sh /usr/local/apache2/create_html.sh
RUN chmod +x /usr/local/apache2/create_html.sh
ENTRYPOINT ["/usr/local/apache2/create_html.sh"]