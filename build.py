import hashlib
import os
import subprocess
import sys

from jinja2 import Environment, FileSystemLoader
import requests


version = sys.argv[1]
build_number = sys.argv[2]


def md5sum(url):
    response = requests.get(url, stream=True)
    hash_md5 = hashlib.md5()
    for chunk in response.iter_content(chunk_size=512):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


context = {
    'version': version,
    'build_number': build_number,
    'description': 'Cloud Station Drive is an application designed to synchronize files between your Synology NAS and PCs via the Internet, ensuring that your data is always up-to-date and enabling you to easily access your files.',
}
build_path = 'builds/{version}-{build_number}'.format(**context)
source_i686 = 'https://global.download.synology.com/download/Tools/CloudStationDrive/{version}-{build_number}/Ubuntu/Installer/i686/synology-cloud-station-drive-{build_number}.i686.deb'.format(**context)
source_x86_64 = 'https://global.download.synology.com/download/Tools/CloudStationDrive/{version}-{build_number}/Ubuntu/Installer/x86_64/synology-cloud-station-drive-{build_number}.x86_64.deb'.format(**context)


context.update({
    'source_i686': source_i686,
    'source_x86_64': source_x86_64,
    'md5sum_i686': md5sum(source_i686),
    'md5sum_x86_64': md5sum(source_x86_64),
})

env = Environment(
    loader=FileSystemLoader('templates'),
)

template = env.get_template('PKGBUILD')

pkgbuild = template.render(**context)


if not os.path.exists(build_path):
    os.makedirs(build_path)

with open('%s/PKGBUILD' % build_path, 'w') as handler:
    handler.write(pkgbuild)

subprocess.run('makepkg --printsrcinfo > .SRCINFO',
               shell=True, cwd=build_path)

