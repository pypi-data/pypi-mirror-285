import argparse
import os
import sys
from cowgirl_ai.load_files.search import Search
from cowgirl_ai.load_files.file_manager import FileManager
from cowgirl_ai.load_files.vector_manager import VectorManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_vector_id():
    """Get vector id for files to be uploaded to."""
    return os.getenv('VECTOR_STORE') # FIX


def search_files(directory, extension):
    """Search a directory for file extensions and add data to 'loaded_files'."""
    stack = Search()
    stack.search(directory, extension)
    return stack.data


def load_files(vector_id):
    """Using the file manager to batch upload loaded files to specific vector."""
    file_manager = FileManager()
    return file_manager.batch_upload(
        vector_id, loaded_files=search_files(
            "src", ".py"))


def load_file(file_name, purpose):
    """Load a singular file, provide full name and upload purpose."""
    file_manager = FileManager()
    return file_manager.upload(file_name, purpose)


def get_load_status(vector_id):
    """Get the load status of files in a vector."""
    vector_manager = VectorManager()
    vector_metadata = vector_manager.get_vector_file_counts(
        vector_id=vector_id
    )
    return vector_metadata


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for file management.")
    subparsers = parser.add_subparsers(dest="command")

    vector_id_parser = subparsers.add_parser(
        "get-vector-id", help="Get vector id for files to be uploaded to")
    vector_id_parser.add_argument(
        "store_name",
        type=str,
        help="Pass the vector name / store name to get id")

    search_parser = subparsers.add_parser(
        "search-files", help="Search a directory for file extensions")
    search_parser.add_argument(
        "directory",
        type=str,
        help="Directory to search")
    search_parser.add_argument(
        "extension",
        type=str,
        help="File extension to search for")

    load_files_parser = subparsers.add_parser(
        "load-files", help="Load files to specific vector")
    load_files_parser.add_argument(
        "vector_id",
        type=str,
        help="Vector ID for file upload")

    load_file_parser = subparsers.add_parser(
        "load-file", help="Load a singular file")
    load_file_parser.add_argument(
        "file_name",
        type=str,
        help="Full name of the file to upload")
    load_file_parser.add_argument(
        "purpose", type=str, help="Purpose of the file upload")

    load_status_parser = subparsers.add_parser(
        "get-load-status", help="Get the load status of files in a vector")
    load_status_parser.add_argument(
        "vector_id",
        type=str,
        help="Vector ID to get load status")

    args = parser.parse_args()

    if args.command == "get-vector-id":
        print(get_vector_id(args.store_name))

    elif args.command == "search-files":
        files = search_files(args.directory, args.extension)
        print(f"Loaded files: {files}")

    elif args.command == "load-files":
        load_files(args.vector_id)
        print(f"Files loaded to vector ID: {args.vector_id}")

    elif args.command == "load-file":
        load_file(args.file_name, args.purpose)
        print(f"File {args.file_name} loaded with purpose: {args.purpose}")

    elif args.command == "get-load-status":
        status = get_load_status(args.vector_id)
        print(f"Load status for vector ID {args.vector_id}: {status}")

# print(main.__module__)