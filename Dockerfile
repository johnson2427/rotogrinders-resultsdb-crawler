# Scrapy runs on Python
FROM python:3.8

# Set the working directory to /usr/src/app
WORKDIR /usr/src/app

# Run install for google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set dates
ARG days1
ARG days2

# set display port to avoid crash
ENV DISPLAY=:99

# set environment variable to days
ENV BUILD_DATE_1=$days1
ENV BUILD_DATE_2=$days2

# Copy the file from the local host to the filesystem of the container at the working
COPY requirements.txt ./

# Install Scrapy specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# copy the project source code from the local host to the filesystem of the container
COPY . .

# Run the crawler when the container launches.requirements
CMD [ "python3", "./main.py"]