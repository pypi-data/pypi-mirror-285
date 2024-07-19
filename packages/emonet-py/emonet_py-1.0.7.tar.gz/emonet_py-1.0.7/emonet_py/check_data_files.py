"""
Check data files exist; if not, download.

.. codeauthor:: Laurent Mertens <laurent.mertens@kuleuven.be>
"""
import os.path
from gitlab import Gitlab
import hashlib
from importlib_metadata import version


class CheckDataFiles:
    PROJECT_ID = '39472331'  # GitLab EmoNet project ID
    URL_START = f'https://gitlab.com/api/v4/projects/{PROJECT_ID}/repository/files/emonet_py%2Fdata%2F'
    URL_END = '/raw?ref=master'

    @classmethod
    def check_and_download(cls):
        # Check data folder exists; if not, create
        abs_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(abs_dir, 'data')
        b_data_folder_exists = os.path.isdir(data_dir)

        if not b_data_folder_exists:
            os.makedirs(data_dir)

        # Check this is a package installation through pip, and we can access the metadata folder
        # Get current package version
        v = version('emonet_py')
        # Attempt to open package metadata folder
        path_metadata = os.path.join(abs_dir, '..', f'emonet_py-{v}.dist-info')
        b_package_install = os.path.isdir(path_metadata)

        # Check expected files exist; if not, download
        expected_files = [
            'conv1.bias.txt.bz2',
            'conv1.weights.txt.bz2',
            'conv2.bias.txt.bz2',
            'conv2.weights.txt.bz2',
            'conv3.bias.txt.bz2',
            'conv3.weights.txt.bz2',
            'conv4.bias.txt.bz2',
            'conv4.weights.txt.bz2',
            'conv5.bias.txt.bz2',
            'conv5.weights.txt.bz2',
            'demo_big.jpg',
            'demo_small.jpg',
            'emonet.pth',
            'fc1.bias.txt.bz2',
            'fc1.weights.txt.bz2',
            'fc2.bias.txt.bz2',
            'fc2.weights.txt.bz2',
            'fc3.bias.txt.bz2',
            'fc3.weights.txt.bz2',
            'img_mean.txt'
        ]

        gl = None
        for file in expected_files:
            # Check file exists and download if not
            path_file = os.path.join(data_dir, file)
            if not (os.path.isfile(path_file)):
                print(f"Attempting to download file {file} from GitLab...", end='', flush=True)
                # Instantiate Gitlab API, if not yet done; this way we don't create an instance, unless one is needed
                if gl is None:
                    gl = Gitlab()
                # Download file
                f = gl.http_get(path=f'{cls.URL_START}{file}{cls.URL_END}')
                with open(path_file, 'wb') as fout:
                    fout.write(f.content)

                # If package install, add file to RECORD metadata file, so that the file will be removed when the
                # package is uninstalled
                if b_package_install:
                    # Get sha256 hash of file, and filesize
                    m = hashlib.sha256()
                    m.update(f.content)
                    file_sha256 = m.hexdigest()
                    file_size = os.path.getsize(path_file)

                    # Append line to RECORD file
                    with open(os.path.join(path_metadata, 'RECORD'), 'a') as fin:
                        fin.write(f'emonet_py/data/{file},sha256={file_sha256},{file_size}\n')

                print(f" done!")


if __name__ == '__main__':
    CheckDataFiles.check_and_download()
