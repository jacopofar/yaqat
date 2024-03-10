FROM python:3.12
# Copy and install the requirements first, so they can be cached
# Since the code will change more often than the requirements
ADD requirements.txt /qa/requirements.txt
RUN pip install --no-cache-dir -r /qa/requirements.txt
ADD . /qa
WORKDIR /qa

CMD ["uvicorn", "--host", "0.0.0.0",  "--port", "8090", "main:app"]