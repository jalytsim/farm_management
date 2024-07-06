#!/bin/bash

# Change to the directory of your Git repository
cd /root/farm_management

# Perform git pull
git pull

# Dump the MySQL database
mysqldump -u brian -pbrian qrcode > /root/farm_management/database/`date +\%d\%m\%Y`.sql
