import shutil
import os

def move_file(source_path, destination_path):
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        final_path = shutil.move(source_path, destination_path)
        print(f"Moved successfully to: {final_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError:
        print("Error: Permission denied.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def copy_file(source_path, destination_path):
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        final_path = shutil.copy(source_path, destination_path)
        print(f"Copied successfully to: {final_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except PermissionError:
        print("Error: Permission denied.")
    except Exception as e:
        print(f"Unexpected error: {e}")


