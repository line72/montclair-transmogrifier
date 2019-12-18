# -*- mode: python -*-
import os
import json
import re

class Web:
    def __init__(self, config):
        self.config = config

    def go(self):
        self.update_readme()
        self.update_package_json()
        self.update_manifest()
        self.update_index()

    def update_readme(self):
        with self.o('README.md', 'w') as f:
            f.write(f'# {self.config.name}\n\n')
            f.write(f'{self.config.description}\n\n')
            f.write(f'{self.config.url}\n')
    
    def update_package_json(self):
        # update the package.json and the package-lock.json
        package = json.loads(self.o('package.json').read())
        # replace the name
        package['name'] = self.config.package_name
        
        with self.o('package.json', 'w') as f:
            f.write(json.dumps(package, indent = 2))
            f.write('\n')

        package_lock = json.loads(self.o('package-lock.json').read())
        # replace the name
        package_lock['name'] = self.config.package_name
        
        with self.o('package-lock.json', 'w') as f:
            f.write(json.dumps(package_lock, indent = 2))
            f.write('\n')

    def update_manifest(self):
        # update the public/manifest.json
        manifest = json.loads(self.o('public/manifest.json').read())

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
        index = self.o('public/index.html').readlines()
        with self.o('public/index.html', 'w') as f:
            for line in index:
                if 'apple-itunes-app' in line:
                    r = re.compile(r'^(.*<meta name="apple-itunes-app" content="app-id=)\w+(">.*)$')
                    matches = r.match(line)
                    if matches:
                        f.write(f'{matches.group(1)}{self.config.ios_config.app_store_id}{matches.group(2)}\n')
                    else:
                        print(sys.stderr, 'Runner.Web: Unable to match apple-itunes-app in public/index.html')
                elif '<title>Montclair</title>' in line:
                    f.write(line.replace('Montclair', self.config.montclair_config.title or self.config.name))
                else:
                    f.write(line)

    def update_first_run(self):
        # Update src/FirstRun.js
        pass

    def update_agency_list(self):
        # Update src/AgencyList.js
        pass

    def update_route_container(self):
        # Update src/RouteContainer.js
        pass
    
    def update_config(self):
        # replace the src/Config.js
        pass

    def o(self, fname, mode = 'r'):
        return open(os.path.join(self.config.build_dir, f'montclair-{self.config.repo}', fname), mode)
