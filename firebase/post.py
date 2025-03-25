from firebase.connection import db
import time

async def reset_projects_collection(new_data):
    """
    Check if the 'projects' collection exists. If it exists, delete it and create a new one with the provided data.

    Parameters:
    new_data (dict): The data to push to the new collection.
    """
    # Reference to the 'projects' collection
    projects_ref = db.collection('projects')

    # Check if the collection exists by trying to get documents
    docs = projects_ref.list_documents()

    start_time = time.time() 
    if docs:
        print("Collection 'projects' exists. Deleting...")
        # Delete all documents in the collection
        for doc in docs:
            doc.delete()  # Delete each document

    # Create a new document in the 'projects' collection with the provided data
    for record in new_data:
        print("Creating new 'projects' collection...")
        projects_ref.add(record)  # Add new record to the collection
    end_time = time.time()

    print(f"New 'projects' collection created successfully. Time took to execute function: {end_time - start_time}")