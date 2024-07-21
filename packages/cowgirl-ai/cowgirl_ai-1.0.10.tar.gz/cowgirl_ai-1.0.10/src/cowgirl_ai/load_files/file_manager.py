"""


https://platform.openai.com/docs/assistants/tools/file-search

"""

from src.cowgirl_ai.load_files.client import Client
import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d",
    format="%(levelname)s - %(asctime)s - %(message)s")


class FileManager(Client):  # pylint: disable=useless-parent-delegation
    """
    For iterating over requests with the OpenAI file storage.
    """

    def __init__(self):  # pylint: disable=useless-parent-delegation
        super().__init__() # pylint: disable=useless-parent-delegation

    def list(self):
        """
        Calls list file method from OpenAI.

        Creates a generator object that iterates over all files
        that persist in authenticated API client.

        Usage::

            >>> file_mgr = FileManager()
        """
        return self.client.files.list()

    def delete_all(self, loaded_files):
        """
        Mass removal of all files associated with an assistant.
        (This helps with maintenance...use with caution)
        """

        logging.info(f"{len(loaded_files)} file(s) are prepped for deletion")
        confirmation = input(
            "Are you sure you want to delete all files? (y/N): ").strip().lower()
        if confirmation == "y":
            for record in loaded_files:
                # API request # TBD Pass on template?
                self.client.files.delete(record)
            logging.info(f"All {len(loaded_files)} records have been deleted")
        else:
            logging.info("Deletion canceled")

    def upload(self, file_name, purpose):
        """
        Upload purpose types:
            - assistants
            - assistants_output
            - batch
            - batch_output
            - fine-tune
            - fine-tune-results
            - vision

        https://platform.openai.com/docs/api-reference/files/object
        """
        return self.client.files.create(
            file=open(file_name, "rb"), purpose=purpose)

    def batch_upload(self, vector_id, loaded_files):
        """
        Batch upload files to a specified vector store.
        One vector store can have many files

        Usage::

            >>> file_manager = FileManager()
            >>> vector_id = vector_ids.get('development_vector')
            >>> file_manager.batch_upload(vector_id)

        """

        try:
            self.file_streams = [open(file, "rb") for file in loaded_files]                 # pylint: disable=attribute-defined-outside-init, consider-using-with
            self.file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(  # pylint: disable=attribute-defined-outside-init
                vector_store_id=vector_id, files=self.file_streams)                         # pylint: disable=attribute-defined-outside-init
            self.batch_status = self.file_batch.status                                      # pylint: disable=attribute-defined-outside-init
            self.batch_file_counts = self.file_batch.file_counts                            # pylint: disable=attribute-defined-outside-init

            logging.info(f"Batch Status: {self.batch_status}")
            logging.info(f"Batch file counts: {self.batch_file_counts}")
            logging.info("Upload complete")
        except Exception as err: # pylint: disable=broad-exception-caught
            logging.error(f"Houston we have a problem: {err}") # pylint: disable=broad-exception-caught


if __name__ == "__main__":
    FileManager()
