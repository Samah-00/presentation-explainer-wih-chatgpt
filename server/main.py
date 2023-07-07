import json
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from sqlalchemy import desc

from server import TIME_FORMAT, DEFAULT_PORT
from utilities import dir_utils, file_utils, request_utils, status_utils
from database.database import session, User, Upload


# create an instance of the Flask class and assigns it to the variable app
app = Flask(__name__)
# set the configuration parameter 'UPLOAD_FOLDER' in app object to the value of UPLOAD_FOLDER
app.config['UPLOAD_FOLDER'] = dir_utils.UPLOAD_FOLDER


def generate_filename(uid, original_filename):
    """
        Generate a new filename by combining the original filename, timestamp, and UID.

        Args:
            uid (str): Unique identifier for the file.
            original_filename (str): Original filename of the uploaded file.

        Returns:
            str: New filename with the format 'uid.pptx'.
    """
    return uid + '.' + original_filename.split('.')[file_utils.FILE_FORMAT_INDEX]


def save_file(file, filename):
    """
       Save the uploaded file to the specified filename in the upload folder.

       Args:
           file (FileStorage): Uploaded file object.
           filename (str): Filename to save the file as.
    """
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


def find_files(files, uid):
    """
        Find files that contain the given UID in the given list.

        Args:
            files (List[str]): List of filenames to search.
            uid (str): Unique identifier to match.

        Returns:
            List[str]: List of filenames that contain the UID.
    """
    # the list comprehension iterates over files and adds a file if it contains the uid in its name
    matching_files = [file for file in files if uid in file]
    return matching_files


def get_explanation_from_file(output_filename):
    """
    Retrieve the explanation from the output file.

    Args:
        output_filename (str): Name of the output file.

    Returns:
        Any: The retrieved explanation.
    """
    with open(os.path.join(dir_utils.OUTPUT_FOLDER, output_filename)) as f:
        explanation = json.load(f)
    return explanation


def create_user(email):
    """
    Create a new User object if it doesn't exist already based on the provided email.

    Args:
        email (str): The email address of the user.

    Returns:
        User: The created or existing User object.
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email)
        session.add(user)
    return user


def create_upload(file, uid, filename, user):
    """
    Create a new Upload object and associate it with the provided user.

    Args:
        file (FileStorage): Uploaded file object.
        uid (str): Unique identifier for the new_upload.
        filename (str): Original filename of the uploaded file.
        user (User): The User object to associate with the new_upload.

    Returns:
        Upload: The created Upload object.
    """
    new_upload = Upload(uid=uid, filename=filename, upload_time=datetime.now(), user=user, status='pending')
    session.add(new_upload)
    session.commit()
    return new_upload


@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle the new_upload endpoint.

    This endpoint receives a POST request with an attached file and optional email parameter.
    It generates a unique identifier (UID) for the uploaded file, saves the file in the 'uploads' folder
    using the UID as the filename, and creates a new Upload object associated with an optional User object
    based on the provided email.
    The Upload object is then committed to the database.
    The endpoint returns a JSON response with the UID of the new_upload.

    Request Parameters:
        - file: The attached file to be uploaded.

    Optional Parameters:
        - email: The email address of the user. If provided, the uploaded file will be associated with this user.

    Returns:
        Response: JSON response with the UID of the new_upload.
    """
    if 'file' not in request.files:
        return jsonify({file_utils.errors['not-found']}), request_utils.RETURN_VALUES['bad-request']

    file = request.files['file']
    uid = str(uuid.uuid4())     # create a unique identifier
    filename = generate_filename(uid, file.filename)
    save_file(file, filename)

    user = None
    if 'email' in request.form:
        email = request.form['email']
        user = create_user(email)

    new_upload = create_upload(file, uid, file.filename, user)

    return jsonify({'uid': uid})


def prepare_response(upload):
    """
    Prepare the response JSON object based on the upload.

    Args:
        upload (Upload): The upload object.

    Returns:
        dict: The response JSON object.
    """
    status = None
    filename = ''
    timestamp = datetime.now()
    explanation = ''

    if upload:
        status = upload.status
        filename = upload.filename
        timestamp = upload.upload_time.strftime(TIME_FORMAT)

        if status == 'done':
            output_files = find_files(os.listdir(dir_utils.OUTPUT_FOLDER), upload.uid)
            if output_files:
                explanation = get_explanation_from_file(output_files[0])

    response = {
        'status': status,
        'filename': filename,
        'timestamp': timestamp,
        'explanation': explanation
    }

    if upload and upload.finish_time:
        response['finish_time'] = upload.finish_time.strftime(TIME_FORMAT)

    return response


@app.route('/status/<uid>', methods=['GET'])
def status(uid):
    """
    Handle the status endpoint.

    This endpoint receives a GET request with a UID as a URL parameter.
    It fetches the corresponding upload from the database based on the provided UID.
    If no matching upload is found, it returns a JSON object with a 'not found' status.
    If a matching upload is found, it checks if there is an associated output file in the database.
    If an output file exists, it retrieves the explanation from the file and sets the status to 'done'.
    If no output file is found, the status is set to 'pending'.
    The endpoint returns a JSON object with the status, original filename, timestamp, explanation (if available),
    and finish time (if available).

    Args:
        uid (str): Unique identifier for the upload.

    Returns:
        Response: JSON response with the status, original filename, timestamp, explanation (if available),
        and finish time (if available).
    """
    upload = session.query(Upload).filter_by(uid=uid).first()
    if not upload:
        return jsonify({'status': 'not found'})

    response = prepare_response(upload)
    return jsonify(response)


@app.route('/get_latest_upload', methods=['GET'])
def get_latest_upload():
    """
    Handle the get_latest_upload endpoint.

    This endpoint receives a GET request with 'filename' and 'email' as URL parameters.
    It fetches the latest upload with the provided filename for the user with the provided email.
    If no matching upload is found, it returns a JSON object with a 'not found' status.
    If a matching upload is found, it returns a JSON object with the status, original filename, timestamp,
    explanation (if available), and finish time (if available).

    Returns:
        Response: JSON response with the status, original filename, timestamp, explanation (if available),
        and finish time (if available).
    """
    filename = request.args.get('filename')
    email = request.args.get('email')

    user = session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({'status': status_utils.STATUS_VALUES['not-found']})

    latest_upload = session.query(Upload).filter_by(user=user, filename=filename).order_by(desc(Upload.upload_time)).first()
    if not latest_upload:
        return jsonify({'status': status_utils.STATUS_VALUES['not-found']})

    response = prepare_response(latest_upload)
    return jsonify(response)


if __name__ == '__main__':
    port = DEFAULT_PORT if os.environ.get('PORT') is None else int(os.environ.get('PORT'))
    app.run(port=port)
