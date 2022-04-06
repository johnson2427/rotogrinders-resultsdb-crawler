# rotogrinders-resultsdb-crawler
## This is a decomissioned repository
Rotogrinders recently changed their results-db site, making this software package obsolete.
It is almost certain that this can be used as a base to pull data from the current resultsdb
to a mongo database (you'll have to change the name of the mongo server).
Since resultsdb has changed so radically, our team has found that this software package is
not required to keep around.

#### Web Scraping Software Package
#### ONLY TESTED ON LINUX MACHINES

## How to install packages:

    $ pip install git+https://github.com/johnson2427/rotogrinders-resultsdb-crawler.git

#### pipenv is required for this package


    (base) user@comp:~/hercules$ pipenv install

    (base) user@comp:~/hercules$ pipenv shell

    (hercules-[vm])(base) user@comp:~/hercules$ pip install -e .


## If Docker is NOT Installed on Your Machine
#### Make sure you have docker-compose installed

    $ sudo apt-get update

    $ sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

#### Deployment Install:

    cd /your/directory/to/hercules
    docker build -t hercules .

#### Run Docker Using ENV variables:

    docker run -e "BUILD_DATE_1='<date1>'" -e "BUILD_DATE_2='<date2>'" rotogrinders-resultsdb-crawler

#### Both <dates> can be the same value.
#### Dates can be in any format

    YYYY-MM-DD
    or
    YYYY/MM/DD
    or
    YYYYMMDD
    etc.






    


