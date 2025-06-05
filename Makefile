.PHONY:do-im
do-im:
	set -ex \
	&& cd app \
	&& docker build -t op2-plapp-image .

.PHONY:do-con-dep
do-con-dep: do-im
	set -ex \
	&& cd app \
	&& docker rm op2-plapp --force \
	&& docker run -d --name op2-plapp -p 8080:80 --env-file ./env.list op2-plapp-image \
	&& docker ps -a 

.PHONY:do-con-dep-e
do-con-dep-e: do-im
	set -ex \
	&& cd app \
	&& docker rm op2-plapp --force \
	&& docker run -d --name op2-plapp -p 8080:80 -e CONFIGURABLE_VALUE=vazurocks! op2-plapp-image \
	&& docker ps -a 

.PHONY: ecr_lin
ecr_lin:
	set -ex \
	&& aws ecr get-login-password --region eu-central-1 | \
	   docker login --username AWS --password-stdin 549665574054.dkr.ecr.eu-central-1.amazonaws.com

.PHONY: test-con
test-con:
	set -ex \
	&& docker rm op2-plapp --force \
	&& docker run -d --name op2-plapp -p 8080:80 549665574054.dkr.ecr.eu-central-1.amazonaws.com/op2-plapp-a770801 \
	&& curl -v localhost:8080

.PHONY:do-cl
do-cl: 
	set -ex \
	&& docker rm op2-plapp --force \
	&& docker image rm op2-plapp-image