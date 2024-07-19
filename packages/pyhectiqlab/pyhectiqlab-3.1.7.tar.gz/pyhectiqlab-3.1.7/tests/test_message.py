import pytest
import os
import time
import logging
logger = logging.getLogger()

@pytest.fixture
def path():
    return os.path.abspath(os.path.join(__file__, "../dummy/artifact.txt"))


def test_messages():

    from pyhectiqlab import functional as hl, Run

    run = Run("Test receiving/publishing messages", project="hectiq-ai/test")
    logger.warning(f"In your bash, type: `HECTIQLAB_API_URL={os.getenv('HECTIQLAB_API_URL')} hectiq-lab Message.publish --run {run.id} --key 'test' --value 'Hello world!'`")
    logger.warning("Waiting for message...")
    msg = None
    while not msg:
        msg = hl.get_message(key="test")
        time.sleep(1)
    if msg:
        logger.warning(f"Received message: {msg}")
        msg.ack()

if __name__ == "__main__":
    test_messages()