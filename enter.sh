#!/bin/bash

# Run to create virtualenv for this repo
# If virtualenv is already created then activate it
# Params:
#   none

ENV_DIRNAME=ai-polit
VIRTUALENV_DIR=$HOME/virtualenv/$ENV_DIRNAME

if [[ ! -d $VIRTUALENV_DIR ]]; then
    virtualenv -p python3 $VIRTUALENV_DIR
    source $VIRTUALENV_DIR/bin/activate
    pip install -r requirements.txt

    # add virtualenv to jupyter
    python -m ipykernel install --user --name=$ENV_DIRNAME
    echo "Please set up your password to jupyter for easier usage:"
    jupyter notebook password
    # See: https://jupyter-dashboards-layout.readthedocs.io/en/latest/getting-started.html
    echo "Configure jupyter dashboard..."
    jupyter dashboards quick-setup --sys-prefix
    # I dont know is it needed?
    jupyter nbextension enable jupyter_dashboards --py --sys-prefix

    # Spacy models

    # used for Lemmatization
    python -m spacy download pl_core_news_sm
    python -m spacy download pl_core_news_md
else
    export PYTHONPATH=$PYTHONPATH:`pwd`
    source $VIRTUALENV_DIR/bin/activate
fi
