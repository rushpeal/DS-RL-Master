# Define base image
FROM continuumio/miniconda3
 
# Set working directory for the project
ENV MAIN_DIRECTORY /usr/src/app

WORKDIR $MAIN_DIRECTORY

# Create Conda environment from the YAML file
COPY . .
RUN conda env create -f env.yml
ENV PATH /opt/conda/envs/lab_env/bin:$PATH

EXPOSE 30000

ENTRYPOINT ["python", "/usr/src/app/main.py", "-p", "30000"]
