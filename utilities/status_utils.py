from collections import namedtuple

# Define a named tuple for the status
Status = namedtuple('Status', ['status', 'filename', 'timestamp', 'explanation', 'finish_time'])

# Define a dictionary for the status values
STATUS_VALUES = {
    'not-found': 'not found',
    'pending': 'pending',
    'done': 'done'
}