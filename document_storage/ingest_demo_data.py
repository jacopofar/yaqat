import logging

import requests

# log with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
if __name__ == '__main__':
    logger = logging.getLogger(__name__)

    filename = 'eng_dist_bodies.csv'
    with open(filename, 'r') as file:
        pending = []
        total_ingested = 0
        for idx, line in enumerate(file):
            # ignore short lines, often spurious
            if len(line) < 100:
                continue
            # remove whitespace and surrounding quotes
            line = line.strip().strip('"').strip()
            pending.append(dict(
                body=line,
                source=f'Line {idx} of file {filename}',
            ))
            if len(pending) > 100:
                response = requests.post(
                    'http://localhost:8000/add_documents',
                    json=pending
                )
                total_ingested += len(pending)
                pending = []
                logger.info(f'Ingested line {idx}, response: {response.text}')
        response = requests.post(
            'http://localhost:8000/add_documents',
            json=pending
        )
        total_ingested += len(pending)
        logger.info(f'Total ingested: {total_ingested}')
