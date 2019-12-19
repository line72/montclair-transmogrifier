import sys
import argparse

from transmogrifier.runners.web import Web
from transmogrifier.runners.ios import IOS
from transmogrifier.runners.android import Android

class Runner:
    def __init__(self, config):
        self.config = config
        self.web = Web(config)
        self.ios = IOS(config)
        self.android = Android(config)

    def go(self):
        self.parse_args()
        
        print('running')
        self.web.go()
        self.ios.go()
        self.android.go()
        
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--env', action = 'store_true',
                            help = 'Write out an ENV file')

        args = parser.parse_args()
        if args.env:
            self.write_env()
            sys.exit(0)
        
    def write_env(self):
        with open('ENV', 'w') as f:
            f.write(f'export BUILD_DIR="{self.config.build_dir}"\n')
            f.write(f'export REPO="{self.config.repo}"\n')
            f.write(f'export VERSION="{self.config.montclair_config.version}"\n')
            f.write(f'export OUTPUT_VERSION="{self.config.montclair_config.version}-{self.config.montclair_config.revision}"\n')
            
            f.write(f'export HAS_IOS={1 if self.config.ios_config else 0}\n')
            if self.config.ios_config:
                f.write(f'export IOS_VERSION="{self.config.ios_config.version}"\n')
                f.write(f'export OUTPUT_IOS_VERSION="{self.config.ios_config.version}-{self.config.ios_config.revision}"\n')
                
            f.write(f'export HAS_ANDROID={1 if self.config.android_config else 0}\n')
            if self.config.android_config:
                f.write(f'export ANDROID_VERSION="{self.config.android_config.version}"\n')
                f.write(f'export OUTPUT_ANDROID_VERSION="{self.config.android_config.version}-{self.config.android_config.revision}"\n')
