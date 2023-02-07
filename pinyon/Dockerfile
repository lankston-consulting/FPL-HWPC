FROM public.ecr.aws/lambda/python:3.9

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target /var/task

# Copy function code
COPY config.json var/runtime/config.json
COPY lambda-function-pinyon.py /var/runtime

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda-function-pinyon.lambda_handler" ] 