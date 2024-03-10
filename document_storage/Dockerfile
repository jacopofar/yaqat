FROM python:3.12
# Copy and install the requirements first, so they can be cached
# Since the code will change more often than the requirements
ADD requirements.txt /document_storage/requirements.txt
RUN pip install --no-cache-dir -r /document_storage/requirements.txt
ADD . /document_storage
WORKDIR /document_storage

CMD ["uvicorn", "--host", "0.0.0.0", "main:app"]