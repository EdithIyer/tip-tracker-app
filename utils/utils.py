import uuid

def generate_uuid_from_columns(*args):
    """
    Generate a UUID based on the values of specified columns.
    
    Args:
    *args: Variable length argument list of column values.
    
    Returns:
    str: A UUID generated based on the input values.
    """
    # Concatenate all arguments into a single string
    combined_string = ''.join(str(arg) for arg in args)
    
    # Generate a UUID using the combined string
    generated_uuid = uuid.uuid5(uuid.NAMESPACE_OID, combined_string)
    
    return str(generated_uuid)
