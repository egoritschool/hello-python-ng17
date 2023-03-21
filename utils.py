import hashlib
import json
import os

ROOT_FILENAME = 'pytest.ini'
FILEHASH_JSON = '.filehash.json'


def project_root():
    """Find project root in parent of CWD"""
    start_dir = os.getcwd()
    cdir = start_dir
    while not os.path.exists(os.path.join(cdir, ROOT_FILENAME)):
        if cdir == '/':
            raise ValueError(f'cannot find project root in parents of {start_dir}. Create {ROOT_FILENAME} it in the project root dir.')
        cdir = os.path.dirname(cdir)
    return cdir


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def not_changed(path):
    root = project_root()
    full_path = os.path.join(root, path)
    if os.path.isdir(full_path):
        raise ValueError(f'path {full_path} should not be directory. It should be regular file')
    json_filename = os.path.join(root, FILEHASH_JSON)

    if not os.path.exists(json_filename):
        saved_hash = None
        file_hashes = {}
    else:
        with open(json_filename) as file:
            file_hashes = json.load(file)
        saved_hash = file_hashes.get(path)

    if not os.path.exists(full_path):
        file_hash = 'NOT_EXIST'
    else:
        file_hash = md5(full_path)
    if not saved_hash:
        file_hashes[path] = file_hash
        with open(json_filename, 'w') as file:
            json.dump(file_hashes, file, indent=2)
        return True
    if file_hash != saved_hash:
        return False
    return True
