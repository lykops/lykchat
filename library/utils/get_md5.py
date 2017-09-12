import hashlib, os

def get_file_md5(filename):
    if not os.path.isfile(filename):
        return False
        
    myhash = hashlib.md5()
    f = open(filename, 'rb')
    while True:
        b = f.read(8096)
        if not b :
            break
        myhash.update(b)
    f.close()
    
    return myhash.hexdigest()
