import time

from client import SystemClient

API_BASE_URL = "http://localhost:8080"
GOOD_FILE = '..\\End_of_course_exercise.pptx'
BAD_FILE = '..\\End_of_course_exercise.txt'
EMAIL_FOR_TEST = 'naruto@gmail.com'

messages = {
    "uid_message": "Uploaded file with UID: ",
    "error_retrieve_data": "Error retrieving data:"
}


def check_status(client, uid):
    while True:
        try:
            status = client.status(uid)
            print(f"Status: {status.status}")
            print(f"Filename: {status.filename}")
            print(f"Timestamp: {status.timestamp}")
            print(f"Explanation: {status.explanation}")
            if status.is_done():
                break  # Exit the loop if the status is 'done'
        except Exception as e:
            error_message = f"{messages['error_retrieve_data']} {e}"
            raise Exception(error_message)  # Raise an exception to indicate test failure
        time.sleep(20)  # Sleep for 20 seconds between iterations


def run_test(filename=None):
    client = SystemClient(API_BASE_URL)
    uid = client.upload(filename)
    if uid is None:
        return
    check_status(client, uid)


def get_latest_upload(client):
    try:
        status = client.get_latest_upload(GOOD_FILE, EMAIL_FOR_TEST)
        print(f"Status: {status.status}")
        print(f"Explanation: {status.explanation}")
        return
    except Exception as e:
        error_message = f"ERROR: {e}"
        raise Exception(error_message)  # Raise an exception to indicate test failure


def run_email_filename_test(filename=None):
    client = SystemClient(API_BASE_URL)
    uid = client.upload(filename, EMAIL_FOR_TEST)
    if uid is None:
        return
    get_latest_upload(client)


def test_normal_case():
    run_test(GOOD_FILE)


def test_wrong_file_extension_case():
    run_test(BAD_FILE)


def test_no_file_case():
    run_test()


def test_email_filename_case():
    run_email_filename_test(GOOD_FILE)
