# Python 2.7 (with all the dependency)
FROM python:2-onbuild

MAINTAINER Contextualist <harzjc@gmail.com>
    
EXPOSE 80
CMD [ "python", "./main.py" ]
