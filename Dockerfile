FROM public.ecr.aws/lambda/python:3.7
COPY . .
RUN python -m pip install --upgrade pip
RUN  pip3 install -r requirements.txt
EXPOSE 8080
CMD [ "application.py" ]