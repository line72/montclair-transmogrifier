# -*- mode: python -*-
import sys
import os
import subprocess
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
        self.update_xcscheme()
        self.update_package_json()
        self.update_config_xml()
        self.update_plist()
        self.update_manifest()
        self.update_ios_json()
        self.update_index()
        self.update_generation_info()
        self.create_icons()
        self.create_splash_screen()

    def update_project_pbx(self):
        # update platforms/ios/Montclair.xcodeproj/project.pbxproj
        #!mwd - Nothing to do...
        pass

    def update_xcscheme(self):
        pass
    
    def update_package_json(self):
        # update the package.json and the package-lock.json
        package = json.loads(self.oread('package.json'))
        # replace the name
        package['name'] = self.config.package_name
        package['displayName'] = self.config.name
        
        with self.o('package.json', 'w') as f:
            f.write(json.dumps(package, indent = 2))
            f.write('\n')

        package_lock = json.loads(self.oread('package-lock.json'))
        # replace the name
        package_lock['name'] = self.config.package_name
        
        with self.o('package-lock.json', 'w') as f:
            f.write(json.dumps(package_lock, indent = 2))
            f.write('\n')

    def update_config_xml(self):
        # update config.xml and platforms/ios/Montclair/config.xml
        for i in ('config.xml', 'platforms/ios/Montclair/config.xml'):
            tree = ET.parse(self.base_path(i))
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
            content.set('src', f'{self.config.url}/index.html')
            
            nav = root.find(f'.//{{{ns}}}allow-navigation')
            if nav:
                nav.set('href', f'{self.config.url}/*')
            
            # write back out
            tree.write(self.base_path(i),
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
        ).replace(
            '<string>Montclair</string>', f'<string>{self.config.name}</string>'
        )

        with self.o('platforms/ios/Montclair/Montclair-Info.plist', 'w') as f:
            f.write(plist)

    def update_manifest(self):
        # Update manifest.json AND www/manifest.json, platforms/ios/www/manifest.json
        for i in ('manifest.json', 'www/manifest.json', 'platforms/ios/www/manifest.json'):
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
        # Update www/index.html
        i = self.oread('www/index.html')
        with self.o('www/index.html', 'w') as f:
            f.write(i.replace('Montclair', self.config.name))

    def update_generation_info(self):
        # Update generationInfo.json
        for i in ('generationInfo.json', 'platforms/ios/generationInfo.json'):
            g = json.loads(self.oread(i))
            g['generatedURL'] = f'{self.config.url}/manifest.json'
            with self.o(i, 'w') as f:
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

        # create a bunch of icons with transparency
        icons = [
            ('AppIcon29x29@2x.png', '58x58'),
            ('AppIcon40x40@2x.png', '80x80'),
            ('icon.png', '57x57'),
            ('icon120-1.png', '120x120'),
            ('icon120.png', '120x120'),
            ('icon152.png', '152x152'),
            ('icon167.png', '167x167'),
            ('icon180.png', '180x180'),
            ('icon20.png', '20x20'),
            ('icon29-1.png', '29x29'),
            ('icon29.png', '29x29'),
            ('icon40-1.png', '40x40'),
            ('icon40-2.png', '40x40'),
            ('icon40.png', '40x40'),
            ('icon58-1.png', '58x58'),
            ('icon58.png', '58x58'),
            ('icon60.png', '60x60'),
            ('icon76.png', '76x76'),
            ('icon80-1.png', '80x80'),
            ('icon80.png', '80x80'),
            ('icon87.png', '87x87'),
            ('icon-20@2x.png', '40x40'),
            ('icon-20@3x.png', '60x60'),
            ('icon-40.png', '40x40'),
            ('icon-40@2x.png', '80x80'),
            ('icon-50.png', '50x50'),
            ('icon-50@2x.png', '100x100'),
            ('icon-60@2x.png', '120x120'),
            ('icon-60@3x.png', '180x180'),
            ('icon-72.png', '72x72'),
            ('icon-72@2x.png', '144x144'),
            ('icon-76.png', '76x76'),
            ('icon-76@2x.png', '152x152'),
            ('icon-83.5@2x.png', '167x167'),
            ('icon@2x.png', '114x114'),
            ('icon-small.png', '29x29'),
            ('icon-small@2x.png', '58x58'),
            ('icon-small@3x.png', '87x87')
            
        ]

        for i in icons:
            subprocess.run(['convert', self.config.logo_svg,
                            '-resize', i[1],
                            self.base_path(f'platforms/ios/Montclair/Images.xcassets/AppIcon.appiconset/{i[0]}')],
                           check = True)

        
        # create icons without transparency
        subprocess.run(['convert', self.config.logo_svg,
                        '-alpha', 'off',
                        '-resize', '1024x1024',
                        self.base_path(f'platforms/ios/Montclair/Images.xcassets/AppIcon.appiconset/icon1024-no-transparency.png')],
                       check = True)


    def create_splash_screen(self):
        icons = [
            ('Default-568h@2x~iphone.png', '640x1136'),
            ('Default-667h.png', '750x1134'),
            ('Default-736h.png', '1242x2208'),
            ('Default@2x~iphone.png', '640x960'),
            ('Default~iphone.png', '320x480'),
            ('Default-Landscape-736h.png', '2208x1242'),
            ('Default-Landscape@2x~ipad.png', '2048x1536'),
            ('Default-Landscape~ipad.png', '1024x768'),
            ('Default-Portrait@2x~ipad.png', '1536x2048'),
            ('Default-Portrait~ipad.png', '768x1024'),
            ('launch_image1024x748.png', '1024x768'),
            ('launch_image1024x768-1.png', '1024x768'),
            ('launch_image1024x768.png', '1024x768'),
            ('launch_image1242x2208.png', '1242x2208'),
            ('launch_image1536x2008.png', '1536x2008'),
            ('launch_image1536x2048-1.png', '1536x2048'),
            ('launch_image1536x2048.png', '1536x2048'),
            ('launch_image2048x1496.png', '2048x1496'),
            ('launch_image2048x1536-1.png', '2048x1536'),
            ('launch_image2048x1536.png', '2048x1536'),
            ('launch_image2208x1242.png', '2208x1242'),
            ('launch_image320x480-9.png', '320x480'),
            ('launch_image640x1136-1.png', '640x1136'),
            ('launch_image640x1136.png', '640x1136'),
            ('launch_image640x960-1.png', '640x960'),
            ('launch_image640x960.png', '640x960'),
            ('launch_image750x1334.png', '750x1334'),
            ('launch_image768x1004.png', '768x1004'),
            ('launch_image768x1024-1.png', '768x1024'),
            ('launch_image768x1024.png', '768x1024')
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
                            self.base_path(f'platforms/ios/Montclair/Images.xcassets/LaunchImage.launchimage/{i[0]}')],
                           check = True)

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
