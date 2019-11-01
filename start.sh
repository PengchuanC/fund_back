#!/bin/zsh

echo Start Server

/usr/bin/python3 manage.py runserver -h 0.0.0.0 -p 5000
