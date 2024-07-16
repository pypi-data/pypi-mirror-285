# Rivalz Python Client

`rivalz-py-client` is a Python client for interacting with the Rivalz API. It allows you to upload files, download files, and manage files on the Rivalz platform using IPFS.

## Features

- **Upload Files**: Upload any file to the Rivalz platform and get an IPFS hash.
- **Upload Passport Images**: Upload passport images to the Rivalz platform.
- **Download Files**: Download files from the Rivalz platform using an IPFS hash.v
- **Delete Files**: Delete files from the Rivalz platform using an IPFS hash.

## Installation

You can install the `rivalz-py-client` package via pip:

```sh
pip install rivalz-py-client
```

## Usage

Here is a detailed guide on how to use the `rivalz-py-client` to interact with the Rivalz API.

### Initialization

First, import the `RivalzClient` class and initialize it with your secret token. If you don't provide a token, it will use a default example token.

```python
from rivalz_client.client import RivalzClient

# Initialize the client with your secret token
client = RivalzClient('your_secret_token')
```

### Uploading a File

To upload a file, use the `upload_file` method. Provide the path to the file you want to upload.

```python
response = client.upload_file('path/to/your/file.txt')
print(response)
```

### Uploading a Passport Image

To upload a passport image, use the `upload_passport` method. Provide the path to the passport image file.

```python
response = client.upload_passport('path/to/your/passport_image.jpg')
print(response)
```

### Downloading a File

To download a file, use the `download_file` method with the IPFS hash of the file and the directory where you want to save the file.

```python
file_path = client.download_file('QmSampleHash', 'save/directory')
print(f"File downloaded to: {file_path}")
```

### Deleting a File

To delete a file, use the `delete_file` method with the IPFS hash of the file you want to delete.

```python
response = client.delete_file('QmSampleHash')
print(response)
```

## Example

Here is a complete example demonstrating how to use the `rivalz-py-client`:

```python
from rivalz_client.client import RivalzClient

# Initialize the client
client = RivalzClient('your_secret_token')

# Upload a file
upload_response = client.upload_file('path/to/your/file.txt')
print(f"Uploaded File Response: {upload_response}")

# Upload a passport image
passport_response = client.upload_passport('path/to/your/passport_image.jpg')
print(f"Uploaded Passport Response: {passport_response}")

# Download a file
   ipfs_hash = 'zdpuB35nxpdDrZibAxWZLVkRepcWLfCbATCUDi5HYYHBwdkZf'  # Replace with the actual IPFS hash
    # Download the file
    try:
        file,filename = client.download(ipfs_hash)
        print(f"File downloaded to: {file}, filename: {filename}")
    except Exception as e:
        print(f"An error occurred during file download: {e}")
# Delete a file
delete_response = client.delete_file('QmSampleHash')
print(f"Delete File Response: {delete_response}")
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a new pull request.



## Publish package


To publish your package, you will need to use `setuptools` and `wheel` to build your package. Here are the steps to follow:

1. Make sure you have `setuptools` and `wheel` installed. If not, you can install them using `pip`:

    ```sh
    pip install setuptools wheel
    ```

2. Create a `setup.py` file in the root directory of your project. This file will contain the metadata about your package, such as its name, version, and dependencies. Here is an example `setup.py` file:

    ```python
    from setuptools import setup, find_packages

    setup(
         name='rivalz-py-client',
         version='1.0.0',
         description='Python client for interacting with the Rivalz API',
         author='Your Name',
         author_email='your_email@example.com',
         packages=find_packages(),
         install_requires=[
              'requests',
         ],
    )
    ```

    Make sure to replace `'Your Name'` and `'your_email@example.com'` with your actual name and email address.

3. Build the package by running the following command:

    ```sh
    python setup.py sdist bdist_wheel
    ```

    This will create a `dist` directory containing the built package files.

4. Upload the package to the Python Package Index (PyPI) using `twine`. If you haven't already, you will need to create an account on PyPI. Once you have an account, you can upload the package by running the following command:

    ```sh
    twine upload dist/*
    ```

    This will upload the package to PyPI, making it available for others to install using `pip`.

That's it! Your package is now published and can be installed by others using `pip install rivalz-py-client`.

Remember to update the version number in your `setup.py` file each time you make changes to your package and want to publish a new version.


### Explanation

- **Project Title**: Clearly states the name of the project.
- **Features**: Lists the main functionalities of the package.
- **Installation**: Provides the command to install the package using `pip`.
- **Usage**: Detailed steps on how to initialize the client, upload files, upload passport images, download files, and delete files.
- **Example**: A complete example script that demonstrates the usage of all the major functionalities.
- **Contributing**: Instructions for contributing to the project.
- **License**: Specifies the license under which the project is released.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
