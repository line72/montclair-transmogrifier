# -*- mode: python -*-
import sys
import os
import json
import re
import shutil
import subprocess

class Web:
    def __init__(self, config):
        self.config = config

    def go(self):
        self.update_readme()
        self.update_package_json()
        self.update_manifest()
        self.update_index()
        self.update_first_run()
        self.update_agency_list()
        self.update_route_container()
        self.update_config()
        self.update_icons()

    def update_readme(self):
        with self.o('README.md', 'w') as f:
            f.write(f'# {self.config.name}\n\n')
            f.write(f'{self.config.description}\n\n')
            f.write(f'{self.config.url}\n')
    
    def update_package_json(self):
        # update the package.json and the package-lock.json
        package = json.loads(self.oread('package.json'))
        # replace the name
        package['name'] = self.config.package_name
        
        with self.o('package.json', 'w') as f:
            f.write(json.dumps(package, indent = 2))
            f.write('\n')

        package_lock = json.loads(self.oread('package-lock.json'))
        # replace the name
        package_lock['name'] = self.config.package_name
        
        with self.o('package-lock.json', 'w') as f:
            f.write(json.dumps(package_lock, indent = 2))
            f.write('\n')

    def update_manifest(self):
        # update the public/manifest.json
        manifest = json.loads(self.oread('public/manifest.json'))

        manifest['short_name'] = self.config.name
        manifest['name'] = self.config.name
        manifest['description'] = self.config.description
        manifest['related_applications'] = []

        if self.config.android_config:
            manifest['related_applications'].append({
                'platform': 'play',
                'url': self.config.android_config.play_store_url,
                'id': self.config.android_config.app_id
            })
        if self.config.ios_config:
            manifest['related_applications'].append({
                'platform': 'itunes',
                'url': self.config.ios_config.app_store_url
            })

        with self.o('public/manifest.json', 'w') as f:
            f.write(json.dumps(manifest, indent = 4))
            f.write('\n')

    def update_index(self):
        # replace the apple-itunes-app in the meta
        # replace the title
        index = self.oreadlines('public/index.html')
        with self.o('public/index.html', 'w') as f:
            for line in index:
                if 'apple-itunes-app' in line:
                    r = re.compile(r'^(.*<meta name="apple-itunes-app" content="app-id=)\w+(">.*)$')
                    matches = r.match(line)
                    if matches:
                        f.write(f'{matches.group(1)}{self.config.ios_config.app_store_id}{matches.group(2)}\n')
                    else:
                        raise Exception('Runner.Web: Unable to match apple-itunes-app in public/index.html')
                elif '<title>Montclair</title>' in line:
                    f.write(line.replace('Montclair', self.config.montclair_config.title or self.config.name))
                else:
                    f.write(line)

    def update_first_run(self):
        # Update src/FirstRunHint.js
        #!mwd - It would be nice if this was a variable...

        first_run = self.oread('src/FirstRunHint.js')

        r = re.compile('^(.*<div className="FirstRunHint.*)Welcome to Birmingham.*?(</div>.*)$', re.MULTILINE | re.DOTALL)
        match = r.match(first_run)
        if match:
            with self.o('src/FirstRunHint.js', 'w') as f:
                f.write(f'{match.group(1)}{self.config.montclair_config.first_run_text}{match.group(2)}')
        else:
            raise Exception('Runner.Web: Unable to match src/FirstRunHint.js')

    def update_agency_list(self):
        # Update src/AgencyList.js and replace Birmingham Transit header
        agencies = self.oreadlines('src/AgencyList.js')

        with self.o('src/AgencyList.js', 'w') as f:
            for line in agencies:
                if 'Birmingham Transit' in line:
                    f.write(line.replace('Birmingham Transit', self.config.montclair_config.title or self.config.name))
                else:
                    f.write(line)

    def update_route_container(self):
        # Update src/RouteContainer.js and replace Birmingham Transit header
        route = self.oreadlines('src/RouteContainer.js')

        with self.o('src/RouteContainer.js', 'w') as f:
            for line in route:
                if 'Birmingham Transit' in line:
                    f.write(line.replace('Birmingham Transit', self.config.montclair_config.title or self.config.name))
                else:
                    f.write(line)
    
    def update_config(self):
        # replace the src/Config.js
        shutil.copy(self.config.montclair_config.configuration_js_file, self.base_path('src/Configuration.js'))

    def update_icons(self):
        # convert the logo.svg into a 512x512 png
        subprocess.run(['convert',
                        '-size', '512x512',
                        'xc:none',
                        '-fill', 'white',
                        '-draw', 'roundRectangle 0,0 512,512 50,50',
                        self.config.logo_svg,
                        '-resize', '512x512',
                        '-compose', 'SrcIn',
                        '-composite',
                        self.base_path('public/app-icon.png')],
                       check = True)

        # convert the logo.svg into a favicon.ico with multiple resolutions
        subprocess.run(['convert',
                        '-size', '256x256',
                        'xc:none',
                        '-fill', 'white',
                        '-draw', 'roundRectangle 0,0 256,256 50,50',
                        self.config.logo_svg,
                        '-resize', '256x256',
                        '-compose', 'SrcIn',
                        '-composite',
                        '-define', 'icon:auto-resize=256,192,152,144,128,96,72,64,48,32,24,16',
                        self.base_path('public/favicon.ico')],
                       check = True)

        # create all the different app-icons
        icons = (
            ('apple-icon', True, (57, 60, 72, 76, 114, 120, 144, 152, 180, 192)),
            ('android-icon', True, (192,)),
            ('favicon', True, (16, 32, 96)),
            ('ms-icon', True, (144,))
        )
        for (i, rounded_corners, sizes) in icons:
            for size in sizes:
                if rounded_corners:
                    corner_ratio = 50 / 512
                    corner_size = int(size * corner_ratio)
                    subprocess.run(['convert',
                                    '-size', f'{size}x{size}',
                                    'xc:none',
                                    '-fill', 'white',
                                    '-draw', f'roundRectangle 0,0 {size},{size} {corner_size},{corner_size}',
                                    self.config.logo_svg,
                                    '-resize', f'{size}x{size}',
                                    '-compose', 'SrcIn',
                                    '-composite',
                                    self.base_path(f'public/{i}-{size}x{size}.png')],
                                   check = True)
                else:
                    subprocess.run(['convert',
                                    self.config.logo_svg,
                                    '-resize', f'{size}x{size}',
                                    self.base_path(f'public/{i}-{size}x{size}.png')],
                                   check = True)

    def base_path(self, fname):
        return os.path.join(self.config.build_dir, f'montclair-{self.config.repo}', fname)

    def o(self, fname, mode = 'r'):
        return open(self.base_path(fname), mode)

    def oread(self, fname):
        with self.o(fname) as f:
            return f.read()

    def oreadlines(self, fname):
        with self.o(fname) as f:
            return f.readlines()
