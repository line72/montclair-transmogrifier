# -*- mode: python -*-

import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import urllib.parse
import json

class Android:
    def __init__(self, config):
        self.config = config

    def go(self):
        if self.config.android_config is None:
            print('Skipping Android PWA creation...', file = sys.stderr)
            return

        self.update_android_json()
        self.update_config_xml()
        self.update_strings_xml()
        self.update_manifest_json()
        self.update_android_manifest()
        self.update_package_name()
        self.update_generation_info()
        self.create_icons()
        self.create_splash_screen()

    def update_android_json(self):
        # Update platforms/android/android.json and plugins/android.json
        for i in ('platforms/android/android.json', 'plugins/android.json'):
            m = self.oread(i)
            m = m.replace('net.line72.montclair', self.config.android_config.app_id)

            with self.o(i, 'w') as f:
                f.write(m)

    def update_config_xml(self):
        # Updates platforms/android/res/xml/config.xml and config.xml
        for i in ('config.xml', 'platforms/android/res/xml/config.xml'):
            tree = ET.parse(self.base_path(i))
            root = tree.getroot()
        
            # register the namespace
            # See: https://stackoverflow.com/questions/3895951/create-svg-xml-document-without-ns0-namespace-using-python-elementtree
            ns = 'http://www.w3.org/ns/widgets'
            ET.register_namespace('', ns)
            ET.register_namespace('cdv', 'http://cordova.apache.org/ns/1.0')
            
            # update the root id and version
            root.set('id', self.config.android_config.app_id)
            root.set('version', self.config.montclair_config.version)
            # find the name, description, and content nodes, allow-navigation and update them
            name = root.find(f'.//{{{ns}}}name')
            name.text = self.config.name
            
            description = root.find(f'.//{{{ns}}}description')
            description.text = self.config.description
            
            content = root.find(f'.//{{{ns}}}content')
            content.set('src', f'{self.config.url}/index.html')
            
            nav = root.find(f'.//{{{ns}}}allow-navigation')
            nav.set('href', f'{self.config.url}/*')
            
            # write back out
            tree.write(self.base_path(i),
                       encoding='utf-8', xml_declaration = True,
                       default_namespace = '')

    def update_strings_xml(self):
        # Update platforms/android/res/values/strings.xml
        p = 'platforms/android/res/values/strings.xml'
        
        tree = ET.parse(self.base_path(p))
        root = tree.getroot()

        name = root.find(f".//string[@name='app_name']")
        name.text = self.config.name
        
        # write back out
        tree.write(self.base_path(p),
                   encoding='utf-8', xml_declaration = True,
                   default_namespace = '')

    def update_manifest_json(self):
        # Update ./platforms/android/assets/www/manifest.json, www/manifest.json, and manifest.json
        for i in ('manifest.json', 'www/manifest.json', 'platforms/android/assets/www/manifest.json'):
            m = json.loads(self.oread(i))
            m['short_name'] = self.config.name
            m['name'] = self.config.name
            m['description'] = self.config.description
            m['start_url'] = self.config.url + '/index.html'

            # fix all the icons
            for icon in m['icons']:
                url = urllib.parse.urlparse(icon['src'])
                icon['src'] = f'{self.config.url}{url.path}'
            
            with self.o(i, 'w') as f:
                f.write(json.dumps(m, indent = 4))
                f.write('\n')

    def update_android_manifest(self):
        # Update ./platforms/android/AndroidManifest.xml
        m = self.oread('platforms/android/AndroidManifest.xml')
        m = m.replace('net.line72.montclair', self.config.android_config.app_id)

        with self.o('platforms/android/AndroidManifest.xml', 'w') as f:
            f.write(m)

    def update_package_name(self):
        # Update the package net.line72.net.montclair in all the java files
        src_dir = os.path.join('platforms', 'android', 'src')

        # First make the new directory based on the package name
        package_path = os.path.join(*self.config.android_config.app_id.split('.'))
        full_path = self.base_path(os.path.join(src_dir, package_path))
        os.makedirs(full_path)
        # Next move move the net/line72/montclair/MainActivity.java to our new package name directory.
        old_path = self.base_path(os.path.join(src_dir, 'net', 'line72', 'montclair'))
        os.rename(os.path.join(old_path, 'MainActivity.java'), os.path.join(full_path, 'MainActivity.java'))
    
        # Then update the package name in:
        # ./platforms/android/src/net/line72/NEW_PACKAGE_NAME/MainActivity.java
        fname = os.path.join(src_dir, package_path, 'MainActivity.java')
        j = self.oread(fname)

        j = j.replace('net.line72.montclair', self.config.android_config.app_id)
        with self.o(fname, 'w') as f:
            f.write(j)

    def update_generation_info(self):
        # update ./generationInfo.json
        g = json.loads(self.oread('generationInfo.json'))
        g['generatedURL'] = f'{self.config.url}/manifest.json'
        with self.o('generationInfo.json', 'w') as f:
            f.write(json.dumps(g, indent = 4))
            f.write('\n')

    def create_icons(self):
        # app-icon.png 512x512
        subprocess.run(['convert',
                        '-size', '512x512',
                        'xc:none',
                        '-fill', 'white',
                        '-draw', 'roundRectangle 0,0 512,512 50,50',
                        self.config.logo_svg,
                        '-resize', '512x512',
                        '-compose', 'SrcIn',
                        '-composite',
                        self.base_path('app-icon.png')],
                       check = True)

        # favicon.ico with multiple resolutions
        subprocess.run(['convert',
                        '-size', '256x256',
                        'xc:none',
                        '-fill', 'white',
                        '-draw', 'roundRectangle 0,0 256,256 25,25',
                        self.config.logo_svg,
                        '-resize', '256x256',
                        '-compose', 'SrcIn',
                        '-composite',
                        '-define', 'icon:auto-resize=256,192,152,144,128,96,72,64,48,32,24,16',
                        self.base_path('favicon.ico')],
                       check = True)

        icons = [
            ('drawable-xxxhdpi/icon.png', '192x192'),
            ('drawable-ldpi/icon.png', '36x36'),
            ('drawable-xhdpi/icon.png', '96x96'),
            ('drawable-xxhdpi/icon.png', '144x144'),
            ('drawable-hdpi/icon.png', '72x72'),
            ('drawable-mdpi/icon.png', '58x58')
        ]
        for i in icons:
            corners = ','.join(i[1].split('x'))
            corner_ratio = 50 / 512
            corner_size = int(int(corners[0]) * corner_ratio)
            subprocess.run(['convert',
                            '-size', i[1],
                            'xc:none',
                            '-fill', 'white',
                            '-draw', f'roundRectangle 0,0 {corners} {corner_size},{corner_size}',
                            self.config.logo_svg,
                            '-resize', i[1],
                            '-compose', 'SrcIn',
                            '-composite',
                            self.base_path(f'platforms/android/res/{i[0]}')],
                           check = True)
    
    def create_splash_screen(self):
        icons = [
            ('drawable-land-xhdpi/screen.png', '1280x720'),
            ('drawable-port-ldpi/screen.png', '200x320'),
            ('drawable-port-mdpi/screen.png', '320x480'),
            ('drawable-port-hdpi/screen.png', '480x800'),
            ('drawable-land-mdpi/screen.png', '400x320'),
            ('drawable-port-xhdpi/screen.png', '720x1280'),
            ('drawable-land-hdpi/screen.png', '800x480'),
            ('drawable-land-ldpi/screen.png', '320x200'),
        ]
        for i in icons:
            w, h = [int(x) for x in i[1].split('x')]
            m = min(w, h)

            # our logo is sqare, so this in the new resolution
            img = int(m / 4)

            # compute the frame, divide by two, since it is on both sides
            frame_w = (w - img) / 2
            frame_h = (h - img) / 2
            
            subprocess.run(['convert', self.config.logo_svg,
                            '-alpha', 'off',
                            '-resize', f'{img}x{img}',
                            '-mattecolor', 'White',
                            '-frame', f'{frame_w}x{frame_h}',
                            self.base_path(f'platforms/android/res/{i[0]}')],
                           check = True)

    def base_path(self, fname):
        return os.path.join(self.config.build_dir, f'montclair-{self.config.repo}-pwa-android', fname)

    def o(self, fname, mode = 'r'):
        return open(self.base_path(fname), mode)

    def oread(self, fname):
        with self.o(fname) as f:
            return f.read()

    def oreadlines(self, fname):
        with self.o(fname) as f:
            return f.readlines()
    
