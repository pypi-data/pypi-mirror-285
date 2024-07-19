from finter.settings import logger
import os


def prepare_docker_submit_files(model_name):
    """
    Copy the poetry.lock and pyproject.toml files to the model directory.
    """

    os.system(f"cp poetry.lock pyproject.toml {model_name}")
    logger.info("Moved poetry.lock and pyproject.toml to model directory.")


    docker_file = """
ARG PYTHON_VERSION

FROM public.ecr.aws/docker/library/python:${PYTHON_VERSION}-slim-bullseye

# Install necessary build tools and libraries
RUN apt-get update && \
    apt-get install -y curl unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install aws cli (x86)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

COPY poetry.lock pyproject.toml /app/

WORKDIR /app

RUN pip install poetry==1.8.3

RUN python -m poetry config virtualenvs.create false  &&  poetry install --no-interaction --no-ansi --no-root
RUN poetry update finter
RUN poetry add pymysql sqlalchemy pytest redis boto3 h5py networkx psutil scipy

COPY . /app
RUN chmod +x /app/submit.sh

CMD ["bash", "/app/submit.sh"]
"""

    file_name = "Dockerfile"

    full_path = os.path.join(model_name, file_name)

    with open(full_path, "w") as file:
        file.write(docker_file)

    logger.info(f"{file_name} saved to {full_path}")

    
    submit_file = """
#!/bin/bash
set -e
set -x

function error_handler {
    echo "Error occurred in script at line: ${BASH_LINENO[0]}"
}

trap error_handler ERR

export PYTHONPATH="/locdisk/code/cc:/locdisk/code/tools:/locdisk/code/model/${MODEL_PATH}:${PYTHONPATH}"

# Create log directory
mkdir -p /locdisk/log/submission

# Create code directory
mkdir -p /locdisk/code

# Copy finter.zip from S3 & unzip
echo "Downloading finter.zip from S3"
aws s3 cp s3://finter-deploy/finter.zip /locdisk/code/finter.zip
ls -al /locdisk/code/
unzip /locdisk/code/finter.zip -d /locdisk/code/
#mv /locdisk/code/cc-master mv /locdisk/code/cc
rm /locdisk/code/finter.zip

echo "Copying files from /app to /locdisk/code/model/${MODEL_PATH}"
mkdir -p /locdisk/code/model/${MODEL_PATH}
cp -r /app/* /locdisk/code/model/${MODEL_PATH}/

# Run python script
echo "Running submit.py"
python /locdisk/code/cc/framework/ops/submission/submit.py
echo "Finished submit.py"
    """

    file_name = "submit.sh"

    full_path = os.path.join(model_name, file_name)

    with open(full_path, "w") as file:
        file.write(submit_file)

    logger.info(f"{file_name} saved to {full_path}")
