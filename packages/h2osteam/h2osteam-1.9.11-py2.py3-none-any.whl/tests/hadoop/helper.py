import h2osteam
import sys
import os

steam_url = 'https://%s:9555' % os.environ['SERVER']


def connect_as_admin():
    try:
        h2osteam.login(url=steam_url,
                       username='admin',
                       password='adminadmin',
                       verify_ssl=False)
    except ConnectionError:
        print('unable to connect to steam runtime on port 9555. '
              'Please ensure the steam-runtime container is running and properly configured.', sys.stderr)


def connect_as_std():
    try:
        h2osteam.login(url=steam_url,
                       username='python',
                       password='python',
                       verify_ssl=False)
    except ConnectionError:
        print('unable to connect to steam runtime on port 9555. '
              'Please ensure the steam-runtime container is running and properly configured.', sys.stderr)


def connect_as_rclient():
    try:
        h2osteam.login(url=steam_url,
                       username='rclient',
                       password='rclient',
                       verify_ssl=False)
    except ConnectionError:
        print('unable to connect to steam runtime on port 9555. '
              'Please ensure the steam-runtime container is running and properly configured.', sys.stderr)
