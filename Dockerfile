FROM python:3.11-slim

# set work directory
WORKDIR /init_tracker

#copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

#copy rest of app
COPY . .

# python will know where to look
ENV PYTHONPATH=/init_tracker

# expose port
EXPOSE 5000

#start app
CMD ["python", "app.py"]
