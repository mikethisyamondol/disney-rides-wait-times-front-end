FROM public.ecr.aws/lambda/python:3.7
WORKDIR /opt/app
COPY . .
RUN python -m pip install --upgrade pip
RUN  pip3 install -r requirements.txt
EXPOSE 5000
CMD [ "application.py" ]