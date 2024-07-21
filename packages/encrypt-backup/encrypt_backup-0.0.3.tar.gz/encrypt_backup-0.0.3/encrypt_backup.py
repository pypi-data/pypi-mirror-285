import os
import sys
import shutil
import hashlib
import subprocess
from curl_cffi import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding


def generate_save_rsa_keys(private_key_path, public_key_path, public_exponent=65537, key_size=4096):
    """
    Generate and save rsa keys,default public exponent is 65537, default key size is 4096
    :param private_key_path: output private key path
    :param public_key_path: output public key path
    :param public_exponent: public exponent
    :param key_size: key size
    :return:
    """
    private_key, public_key = __generate_rsa_keys()
    __save_rsa_keys(*__generate_rsa_keys(public_exponent, key_size), private_key_path, public_key_path)


def compress_and_encrypt_folder(backup_file_path, encrypted_7zip_path, public_key_path, base_path=None):
    """
    Compress and encrypt folder,only support rsa public key
    :param backup_file_path: folder or file path that you want to backup
    :param encrypted_7zip_path: output file path
    :param public_key_path: rsa public key path
    :param base_path: envrionment path, default is None
    :return:
    """
    if not __check_7z_installed():
        if not __is_debian_or_ubuntu():
            print("7z is not installed,and system not support auto install 7z. Please install 7z manually.")
            sys.exit(0)
        __install_7z()
    public_key = __load_public_key(public_key_path)
    backup_folder = os.path.join(base_path, "backup")
    if os.path.exists(backup_folder):
        shutil.rmtree(backup_folder)
    shutil.copytree(backup_file_path, backup_folder)
    print("Copy files to backup folder done")
    zip_command = ['7z', 'a', '-t7z', '-mx=9', 'tmp.7z', backup_folder]
    process = subprocess.Popen(zip_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 实时打印压缩过程的输出
    for line in process.stdout:
        print(line.strip())

    process.wait()

    if process.returncode != 0:
        raise Exception(f"Error occurred during zip: {process.stderr.read()}")
    tmp_file_path = os.path.join(base_path, "tmp.7z")
    with open(tmp_file_path, 'rb') as f:
        zip_data = f.read()

    aes_key = os.urandom(32)
    aes_iv = os.urandom(16)

    # 使用 AES 加密数据
    encrypted_data = __aes_encrypt(aes_key, aes_iv, zip_data)

    # 使用 RSA 加密 AES 密钥和 IV
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    encrypted_aes_iv = public_key.encrypt(
        aes_iv,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    with open(encrypted_7zip_path, 'wb') as f:
        f.write(encrypted_aes_key)
        f.write(encrypted_aes_iv)
        f.write(encrypted_data)
    os.remove(tmp_file_path)
    shutil.rmtree(backup_folder)


def decrypt_file(source_file_path, output_file_path, private_key_path):
    """
    Decrypt file,only support rsa private key
    :param source_file_path:
    :param output_file_path:
    :param private_key_path:
    :return:
    """
    private_key = __load_private_key(private_key_path)
    with open(source_file_path, 'rb') as f:
        modulus = private_key.private_numbers().public_numbers.n
        bit_length = modulus.bit_length()
        byte_length = (bit_length + 7) // 8
        encrypted_aes_key = f.read(byte_length)
        encrypted_aes_iv = f.read(byte_length)
        encrypted_data = f.read()

    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aes_iv = private_key.decrypt(
        encrypted_aes_iv,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # 使用 AES 密钥和 IV 解密数据
    decrypted_data = __aes_decrypt(aes_key, aes_iv, encrypted_data)
    with open(output_file_path, 'wb') as f:
        f.write(decrypted_data)


def upload_file_to_alist(alist_url, local_file_path, remote_file_path, auth_token=None, auth_user=None,
                         auth_password=None):
    """
    Upload file to Alist,chose auth_token or auth_user and auth_password to login alist
    :param alist_url: example: https://alist-demo.alist.org,do not include / at the end
    :param local_file_path: file path that you want to upload
    :param remote_file_path: alist file path that you want to save
    :param auth_token: auth token
    :param auth_user: auth user
    :param auth_password: auth password
    :return: None if failed, else return response json
    """
    sess = requests.Session(impersonate="chrome120")
    url = f"{alist_url}/api/fs/put"

    with open(local_file_path, "rb") as f:
        payload = f.read()
    if auth_token:
        token = auth_token
    elif auth_user and auth_password:
        auth_url = f"{alist_url}/api/auth/login/hash"
        auth_payload = {
            "username": auth_user,
            "password": __hash_string_sha256(
                auth_password + "-https://github.com/alist-org/alist")
        }
        response = sess.post(auth_url, json=auth_payload).json()
        if response.get("code") == 200:
            token = response["data"]["token"]
        else:
            print("auth failed")
            return None
    else:
        print("Please provide auth_token or auth_user and auth_password")
        return None
    headers = {
        'Authorization': token,
        'File-Path': remote_file_path.encode("utf-8"),
        'As-Task': 'true',
        'Content-Length': str(len(payload)),
        'Content-Type': 'application/octet-stream'
    }

    sess.headers.update(headers)

    response = sess.put(url, data=payload, timeout=600000)

    return response.json()


def __generate_rsa_keys(public_exponent=65537, key_size=4096):
    private_key = rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def __save_rsa_keys(private_key, public_key, private_key_path, public_key_path):
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(private_key_path, 'wb') as private_file:
        private_file.write(pem_private_key)

    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_key_path, 'wb') as public_file:
        public_file.write(pem_public_key)


def __is_root_user():
    return os.geteuid() == 0


def __is_debian_or_ubuntu():
    try:
        with open("/etc/os-release") as file:
            content = file.read()
            return "ID=debian" in content or "ID=ubuntu" in content
    except FileNotFoundError:
        return False


def __check_7z_installed():
    try:
        # 尝试执行7z命令
        subprocess.run(["7z", "--help"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 如果执行失败，返回False
        return False


def __install_7z():
    if not __is_root_user():
        print("Please run this script as root.")
        sys.exit(0)
    try:
        print("Attempting to install 7z with apt...")
        subprocess.run(["apt", "update"], check=True)
        subprocess.run(["apt", "install", "-y", "p7zip-full"], check=True)
        print("7z installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Installation failed. Please install 7z manually.", file=sys.stderr)


def __aes_encrypt(key, iv, data):
    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(padded_data) + encryptor.finalize()


def __load_public_key(public_key_path):
    with open(public_key_path, 'rb') as public_file:
        public_key = serialization.load_pem_public_key(
            public_file.read(),
            backend=default_backend()
        )
    return public_key


def __hash_string_sha256(input_string):
    input_bytes = input_string.encode('utf-8')

    hash_object = hashlib.sha256(input_bytes)

    hash_hex = hash_object.hexdigest()

    return hash_hex


def __load_private_key(private_key_path):
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def __aes_decrypt(key, iv, data):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(data) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data
