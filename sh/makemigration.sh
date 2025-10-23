#!/bin/bash

if [ "$#" -gt 0 ]; then
  alembic revision --autogenerate -m "$1"
else
  echo "should input message"
fi