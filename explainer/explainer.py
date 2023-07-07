import os
import json
from collections import namedtuple
import asyncio
import time
import logging
from datetime import datetime

from database.database import Upload, session

from presentation.my_presentation import MyPresentation
from utilities import dir_utils, file_utils, status_utils

messages = {
    "no_unprocessed_files": "No unprocessed files found. Waiting for new files...",
    "invalid_file": "Invalid file path or unsupported file extension.",
    "process_success": "File processed successfully: ",
    "saved": "Explanation saved: "
}


async def main(pptxfile):
    """
    Main function to generate explanations for each slide in a PowerPoint presentation.

    Args:
        pptxfile (str): The path to the PowerPoint file.

    Generates explanations for each slide in the PowerPoint presentation, stores them in a list of namedtuples,
    and saves the explanations to a JSON file.

    The explanations are stored as namedtuples with fields 'slide_number' and 'explanation'.

    The JSON file is saved with the same name as the PowerPoint file, but with the extension '.json'.

    Example usage:
        asyncio.run(main("presentation.pptx"))
    """
    presentation = MyPresentation(filepath=pptxfile)
    presentation.parse()

    Explanations = namedtuple('Explanations', ['slide_number', 'explanation'])
    presentation.explanations = []

    for slide_number, slide in presentation.slides.items():
        explanation = await slide.generate_explanation()
        explanation_entry = Explanations(slide_number=slide_number, explanation=explanation)
        presentation.explanations.append(explanation_entry)

    return presentation


def process_upload_file(upload, file_path):
    """
    Process an upload file.

    Args:
        upload (Upload): The upload object from the database.
        file_path (str): The path to the upload file.

    Process the file, generate explanations, save the output file, and update the upload status and finish time.
    """
    if os.path.isfile(file_path) and \
            os.path.splitext(upload.filename)[1].lower() == file_utils.PRESENTATION_FILE_EXTENSION:
        try:
            logging.info(f"Processing file {upload.filename}")
            presentation = asyncio.run(main(file_path))
        except Exception as e:
            logging.error(f"Error processing file: {upload.filename}. Error: {e}")
            return

        output_file_path = os.path.join(dir_utils.OUTPUT_FOLDER, f'{upload.uid}{file_utils.OUTPUT_FILE_EXTENSION}')
        with open(output_file_path, 'w') as f:
            json.dump(presentation.explanations, f, indent=4)

        return output_file_path  # Return the output file path
    else:
        logging.warning(f'{upload.filename}: {messages["invalid_file"]}')


def update_upload_status(upload):
    """
    Update the status and finish time of the processed upload in the database.

    Args:
        upload (Upload): The upload object from the database.
    """
    upload.status = status_utils.STATUS_VALUES['done']
    upload.finish_time = datetime.now()
    session.add(upload)  # Add the upload to the session
    session.commit()  # Commit the changes


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='{asctime} {levelname} {message}', style='{')

    while True:
        # Fetch pending uploads from the database
        pending_uploads = session.query(Upload).filter_by(status=status_utils.STATUS_VALUES['pending']).all()

        if not pending_uploads:
            # If no pending uploads found, print a message and continue to the next iteration
            logging.info(messages["no_unprocessed_files"])
            time.sleep(10)
            continue

        for upload in pending_uploads:
            file_path = os.path.join(dir_utils.UPLOAD_FOLDER, upload.filename)
            output_file_path = process_upload_file(upload, file_path)
            if output_file_path:
                update_upload_status(upload)
                logging.info(f"{messages['process_success']}{upload.filename}")
                logging.info(f"{messages['saved']}{output_file_path}")

        # Sleep for a few seconds before the next iteration
        time.sleep(10)
