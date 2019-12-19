# -*- mode: python -*-
import sys
import os
import io
import xml.etree.ElementTree as ET
import urllib.parse
import json

class IOS:
    def __init__(self, config):
        self.config = config

    def go(self):
        if self.config.ios_config is None:
            print('Skipping iOS PWA creation...', file = sys.stderr)
            return

        self.update_project_pbx()
        self.update_config_xml()
        self.update_plist()
        self.update_manifest()
        self.update_ios_json()
        self.update_index()
        self.update_config_xml2()
        self.update_ios_json2()
        self.update_generation_info()
        self.create_icons()
        self.create_splay_screen()

    def update_project_pbx(self):
        # update platforms/ios/Montclair.xcodeproj/project.pbxproj
        pass

    def update_config_xml(self):
        # update platforms/ios/Montclair/config.xml
        tree = ET.parse(self.base_path('platforms/ios/Montclair/config.xml'))
        root = tree.getroot()
        
        # register the namespace
        # See: https://stackoverflow.com/questions/3895951/create-svg-xml-document-without-ns0-namespace-using-python-elementtree
        ns = 'http://www.w3.org/ns/widgets'
        ET.register_namespace('', ns)
        ET.register_namespace('cdv', 'http://cordova.apache.org/ns/1.0')

        # update the root id and version
        root.set('id', self.config.ios_config.app_id)
        root.set('version', self.config.montclair_config.version)
        # find the name, description, and content nodes, allow-navigation and update them
        name = root.find(f'.//{{{ns}}}name')
        name.text = self.config.name

        description = root.find(f'.//{{{ns}}}description')
        description.text = self.config.description

        content = root.find(f'.//{{{ns}}}content')
        content.set('src', self.config.url)

        nav = root.find(f'.//{{{ns}}}allow-navigation')
        nav.set('href', f'{self.config.url}/*')
        
        # write back out
        tree.write(self.base_path('platforms/ios/Montclair/config.xml'),
                   encoding='utf-8', xml_declaration = True,
                   default_namespace = '')

    def update_plist(self):
        # Update platforms/ios/Montclair/Montclair-Info.plist

        url = urllib.parse.urlparse(self.config.url).netloc
        
        plist = self.oread('platforms/ios/Montclair/Montclair-Info.plist')
        plist = plist.replace(
            'net.line72.montclair', self.config.ios_config.app_id
        ).replace(
            'montclair.line72.net', url
        )

        with self.o('platforms/ios/Montclair/Montclair-Info.plist', 'w') as f:
            f.write(plist)

    def update_manifest(self):
        # Update manifest.json AND www/manifest.json
        for i in ('manifest.json', 'www/manifest.json'):
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

    def update_ios_json(self):
        # update platforms/ios/ios.json and plugins/ios.json
        for i in ('platforms/ios/ios.json', 'plugins/ios.json'):
            r = self.oread(i)
            r = r.replace('net.line72.montclair', self.config.ios_config.app_id)

            with self.o(i, 'w') as f:
                f.write(r)

    def update_index(self):
        pass

    def update_config_xml2(self):
        pass

    def update_ios_json2(self):
        pass

    def update_generation_info(self):
        pass

    def create_icons(self):
        pass

    def create_splay_screen(self):
        pass

    def base_path(self, fname):
        return os.path.join(self.config.build_dir, f'montclair-{self.config.repo}-pwa-ios', fname)

    def o(self, fname, mode = 'r'):
        return open(self.base_path(fname), mode)

    def oread(self, fname):
        with self.o(fname) as f:
            return f.read()

    def oreadlines(self, fname):
        with self.o(fname) as f:
            return f.readlines()
