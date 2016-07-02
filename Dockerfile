# Python 2.7 (with all the dependency), Daocloud source
FROM daocloud.io/python:2-onbuild

MAINTAINER Contextualist <harzjc@gmail.com>
    
EXPOSE 80
CMD [ "python", "./main.py" ]
