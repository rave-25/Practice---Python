#   block size - 4096 bytes
#   from files to number of bytes 

def calculate_storage(filesize):
    block_size = 4096
    # Use floor division to calculate how many blocks are fully occupied
    full_blocks = filesize//block_size
    partial_block_remainder = filesize%block_size
    if partial_block_remainder > 0:
        return block_size*(full_blocks+1)
    return full_blocks*block_size

print(calculate_storage(1)) 