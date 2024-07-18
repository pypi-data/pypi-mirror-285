# import asyncio
import websockets
import asyncclick as click
import ssl
import json
import itertools
import sys
import time
import threading

# Disable SSL
ssl_context = ssl._create_unverified_context()


# Creates a spinner at the bottom of the cli to visualise activity
class SpinnerThread(threading.Thread):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.spinner_chars = itertools.cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
        self.running = True
        self.start_time = time.time()

    def run(self):
        print(self.message)
        while self.running:
            elapsed_time = int(time.time() - self.start_time)
            sys.stdout.write(f'\r{next(self.spinner_chars)} Executing Test (Elapsed Time: {elapsed_time}s)')
            sys.stdout.flush()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        sys.stdout.write('\r \r')  # Clear the spinner line
        sys.stdout.flush()


# Get the websocket
def get_websocket():
    # Get the current context object
    ctx = click.get_current_context()

    # Check if a WebSocket connection is active
    if ctx.obj and hasattr(ctx.obj, 'websocket'):
        websocket = ctx.obj.websocket
    else:
        # If no WebSocket connection is active, create a new one
        websocket = None
    return websocket


# Disconnection Function
async def disconnect(websocket):
    try:
        # Send a disconnect message to the WebSocket server
        await websocket.send(json.dumps({'action': 'disconnect'}))

        # Close the WebSocket connection
        await websocket.close()
        return True
    except Exception:
        return False


# Function to start a single test
async def start_test(websocket, test_id, job_name, job_description):
    """
    Handles the JSON response received from the WebSocket connection.

    Args:
        response (str): The JSON response string received from the WebSocket.

    Returns:
        str: The job ID extracted from the JSON response.
    """
    await websocket.send(json.dumps(
        {
            'action': 'startTest',
            'testId': test_id,
            'jobName': job_name,
            'jobDescription': job_description,
        }
    ))

    # Handle the response and extract the job_id
    response = await websocket.recv()
    json_response = json.loads(response)
    json_body = json.loads(json_response.get('body', '{}'))
    job_id = json_body.get('job_id')

    return job_id


# Function to start a batch of tests
async def start_batch_test(websocket, test_ids):
    # Make a request to your backend service to start the batch of tests
    test_ids_str = ' '.join(test_ids)
    await websocket.send(f'startBatchTest {test_ids_str}')

    # Handle the response and extract the job_id
    job_id = await websocket.recv()
    return job_id


# Function to get the status of a single test
async def get_test_status(websocket, job_id):
    # Start the spinner thread
    spinner_thread = SpinnerThread('')
    spinner_thread.start()

    try:
        # Send a request to listen for test status updates
        await websocket.send(json.dumps({'action': 'jobStatus', 'testId': job_id}))

        # Listen for test status updates
        while True:
            status_update = await websocket.recv()
            json_response = json.loads(status_update)
            json_body = json.loads(json_response.get('body', '{}'))
            message = json_body.get('message', None)

            if message:
                status = message.split(' | ')[1]
                msg_string = message.split(' | ')[2]

            errorMessage = json_body.get('errorMessage', None)

            if errorMessage:
                sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
                print(f'Error: {errorMessage}')
                disconnect(get_websocket())
                sys.exit(1)
            else:
                if msg_string == 'complete':
                    sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
                    print('Test complete')
                    break
                elif status == 'failed':
                    sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
                    print(message)
                    sys.exit(1)
                else:
                    sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear the line
                    print(message)
    finally:
        spinner_thread.stop()
        spinner_thread.join()


# Function to get the status of a batch of tests
async def get_batch_test_status(websocket, job_id):
    # Send a request to listen for batch test status updates
    await websocket.send(f'batchTestStatus {job_id}')

    # Listen for batch test status updates
    while True:
        status_update = await websocket.recv()
        if status_update == 'complete':
            break
        else:
            print(status_update)


def test_id_required(ctx, param, value):
    if value is None:
        raise click.BadParameter('--test-id is required', ctx=ctx)
    return value


@click.group()
async def cli():
    pass


@cli.command(name='start-test')
@click.option('--test-id', type=str, callback=test_id_required, help='The UUID of the test to start.')
@click.option('--job-name', required=True, help='Add a Job Name for easier reporing.')
@click.option('--job-description', help='Provide a description for the job.')
@click.option('--url', required=True, help='The WebSocket URL to connect to.')
@click.option('--api-key', required=True, help='The API key for authentication.')
async def start_test_cmd(test_id, url, api_key, job_name, job_description):
    async with websockets.connect(url, ssl=ssl_context, extra_headers={'x-api-key': api_key}) as websocket:
        job_id = await start_test(websocket, test_id, job_name, job_description)
        print(f'Started test with job ID: {job_id}')
        await get_test_status(websocket, job_id)


@cli.command(name='start-batch-test')
@click.option('--test-ids', multiple=True, type=str, help='The UUIDs of the tests to start.')
@click.option('--url', required=True, help='The WebSocket URL to connect to.')
@click.option('--api-key', required=True, help='The API key for authentication.')
async def start_batch_test_cmd(test_ids, url, api_key):
    async with websockets.connect(url, ssl=ssl_context, extra_headers={'x-api-key': api_key}) as websocket:
        job_id = await start_batch_test(websocket, test_ids)
        print(f'Started batch test with job ID: {job_id}')


@cli.command(name='get-test-status')
@click.option('--job-id', type=str, help='The job ID of the test to get status for.')
@click.option('--url', required=True, help='The WebSocket URL to connect to.')
@click.option('--api-key', required=True, help='The API key for authentication.')
async def get_test_status_cmd(job_id, url, api_key):
    async with websockets.connect(url, ssl=ssl_context, extra_headers={'x-api-key': api_key}) as websocket:
        await get_test_status(websocket, job_id)


@cli.command(name='get-batch-test-status')
@click.option('--job-id', type=str, help='The job ID of the batch test to get status for.')
@click.option('--url', required=True, help='The WebSocket URL to connect to.')
@click.option('--api-key', required=True, help='The API key for authentication.')
async def get_batch_test_status_cmd(job_id, url, api_key):
    async with websockets.connect(url, ssl=ssl_context, extra_headers={'x-api-key': api_key}) as websocket:
        await get_batch_test_status(websocket, job_id)


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print("CTRL-C pressed, interrupted connection.")
        print('Closing Connection.')

        disconnect(get_websocket())
    finally:
        sys.exit(0)
