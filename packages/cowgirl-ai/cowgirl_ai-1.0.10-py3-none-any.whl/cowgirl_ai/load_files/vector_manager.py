"""
https://platform.openai.com/docs/api-reference/vector-stores/create
"""

from src.cowgirl_ai.load_files.client import Client
import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt="%Y-%m-%d",
    format="%(levelname)s - %(asctime)s - %(message)s")


class VectorManager(Client):
    """
    For interacting with the OpenAI client for VectorManager
    """

    def __init__(self):
        super().__init__()
        self.data = []

    def list(self):
        return self.client.beta.vector_stores.list()

    def add_record(self, *args):
        """
        Stack data structure for processing file_ids / mass updates.

        File ID is a consistent paramater used for deleting, updating, retrieving
        files.

        Usage::

            >>> file_manager = FileManager()
            >>> file_manager.process_file_ids()
            >>> print(file_manager.file_ids)

        """
        if len(args) != 1:
            raise ValueError(
                "Two arguments are required: directory and file extension.")
        return self.data.append(args)

    def delete_all(self):
        """
        Mass removal of all files associated with an assistant.
        (This helps with maintenance...use with caution)
        """

        files = self.list()
        for file in files:
            self.add_record(file)

        confirmation = input(
            "Are you sure you want to delete all? (y/N): ").strip().lower()
        if confirmation == "y":
            for record in self.data:
                self.client.beta.vector_stores.delete(record)
            logging.info(f"All {len(self.data)} records have been deleted")
        else:
            logging.info("Deletion canceled")

    def create_new_vector_store(self, name):
        """
        Taking a provided name as an input, generate a new vector store
        Note: takes a while, use with caution.

        # data generation vector id: vs_B8b8I9KVk56YJgOOMWTt4KEz
        # development vector id: vs_BpS14hR5vN5BXZ1SQq5uWMoW
        # production vector id: vs_v0FNOqKwDYSKwPPMnqKRnRD7
        """

        return self.client.beta.vector_stores.create(name=name)

    def retrieve_vector(self, vector_id):
        """
        Returns data for a specific vector id.
        Includes information such as status, file counts. Useful for monitoring information and process.
        """

        return self.client.beta.vector_stores.retrieve(
            vector_store_id=vector_id)

    def get_vector_file_counts(self, vector_id):
        """
        Gets file counts attribute
        """

        vector_store = self.retrieve_vector(vector_id)
        file_counts = vector_store.file_counts
        logging.info(
            f"""Vector File Counts
                      cancelled: {file_counts.cancelled},
                      in progress: {file_counts.in_progress},
                      completed: {file_counts.completed},
                      failed: {file_counts.failed},

        """
        )
        return file_counts


if __name__ == "__main__":
    # One vector store can have many files
    # Vectors align with different types of assistants, and should be immutable
    # Use 'development vector' id for testing
    VectorManager()
