#!/bin/bash
# Script to help the use of the GoCD Environment Manager Application - GEMA
# qaas@stone.com.br, May 2017
#
# Use: ./manager.sh <action> <environment> <pipeline>
#   action: list | add | remove
#   environment: the name of the environment you want to manage
#   pipeline: the name of the pipeline you want to add or remove to an environment
#
# Example:
# ./gema.sh list Dev My_Pipeline

ACTION=$1
ENVIRONMENT=$2
PIPELINE=$3

APP_URL="https://gema.stone.com.br"
#APP_URL="http://localhost:8888"

if [ $# -eq 3 ]; then
    curl "$APP_URL/$ACTION?env=$ENVIRONMENT&pipeline=$PIPELINE"
else
    echo "Use: ./gema.sh <action> <environment> <pipeline>"
    echo "  action: list | add | remove"
    echo "  environment: the name of the environment you want to manage"
    echo "  pipeline: the name of the pipeline you want to add or remove to an environment"
fi
