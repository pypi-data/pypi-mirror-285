

import os
import sys
import re
import argparse
import urllib.request

from html.parser import HTMLParser
from xml.etree import ElementTree as ET

class _RSS():

    def __init__(self):
        """ _RSS()

        parse rss feed extracting channel contents
        """
        self.rdict={}
        self.rdict['items'] = []

    def channel(self, root):
        """ channel(root)

        parse an rss channel
        root - root of the channel xml tree
        """
        for child in root:
            tag = child.tag
            taga = re.split('[{}]', child.tag)
            if len(taga) == 3:
                tag = taga[2]
            if tag == 'item':
                ih = self.item(child)
                self.rdict['items'].append(ih)

    def html(self, htmlfrag):
        html = htmlfrag
        if 'html' not in htmlfrag:
           html = '<html>%s</html>' % (htmlfrag)
        class MyHTMLParser(HTMLParser):
            def __init__(self):
                    super().__init__()
                    self.dicta = []
                    self.src = None

            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    for tpl in attrs:
                        if tpl[0] == 'href':
                            d={}
                            if hasattr(self, 'src'):
                                if re.match('^\s+$', self.src):
                                    self.src = ''
                                d['data'] = self.src
                                d['href'] = tpl[1]
                            else:
                                d['data'] = ''
                                d['href'] = tpl[1]
                            self.dicta.append(d)
            def handle_data(self, data):
                    self.src = data
        parser = MyHTMLParser()
        parser.feed(html)
        return parser.dicta

    def item(self, root):
        """ item(root)

        parse an item in a channel
        root - root of the item xml tree
        """
        ih = {}
        for child in root:
            tag = child.tag
            taga = re.split('[{}]', child.tag)
            if len(taga) == 3:
                tag = taga[2]
            if tag == 'media:content':
                continue
            elif '</a>' in child.text:
                ih[tag] = []
                dicta = self.html(child.text)
                ih[tag] = dicta
            else:
                if tag in ih.keys():
                    ih[tag] = '%s,%s' % (ih[tag], child.text)
                else:
                    ih[tag] = child.text
        return ih

    def reportrss(self, rdict):
        for i in range(len(rdict['items']) ):
            item = rdict['items'][i]
            for k in item.keys():
                if item[k]:
                    print('item %d %s: %s' % (i, k, item[k]) )

    def feed(self, rstr):
        """ feed(root)

        parse an rss feed
        root - root of the rss xml tree
        """
        xroot = ET.fromstring(rstr)
        for child in xroot:
            tag = child.tag
            taga = re.split('[{}]', child.tag)
            if len(taga) == 3:
                tag = taga[2]
            if tag == 'channel':
                self.channel(child)
            else: rdict[tag] = child.text
        return self.rdict


class _Atom():

    def __init__(self):
        self.adict = {}
        self.adict['entries'] = []

    def html(self, htmlfrag):
        html = htmlfrag
        if 'html' not in htmlfrag:
           html = '<html>%s</html>' % (htmlfrag)
        class MyHTMLParser(HTMLParser):
            def __init__(self):
                    super().__init__()
                    self.dicta = []
                    self.src = None

            def handle_starttag(self, tag, attrs):
                if tag == 'a':
                    for tpl in attrs:
                        if tpl[0] == 'href':
                            d={}
                            if hasattr(self, 'src'):
                                #if re.match('^\s+$', self.src):
                                #    self.src = ''
                                d['data'] = self.src
                                d['href'] = tpl[1]
                            else:
                                d['data'] = 'entry'
                                d['href'] = tpl[1]
                            self.dicta.append(d)
            def handle_data(self, data):
                    self.src = data
        parser = MyHTMLParser()
        parser.feed(html)
        return parser.dicta

    def entry(self, root):
        ea = []
        #print('%s %s' % (root.tag, root.text), file=sys.stderr )
        for child in root:
            eh = {}
            tag = child.tag
            taga = re.split('[{}]', child.tag)
            if len(taga) == 3:
                tag = taga[2]
            if not child.text:
                continue
            if '</a>' in child.text:
                eh[tag] = []
                dicta = self.html(child.text)
                eh[tag] = dicta
            else:
                if tag in eh.keys():
                    eh[tag] = '%s,%s' % (eh[tag], child.text)
                else:
                    eh[tag] = child.text
            ea.append(eh)
        #print('atom entry number stories %d' % (len(ea) ),
        #     file=sys.stderr )
        return ea

    def reportatom(self):
        edict = self.adict['entries']
        for i in range(len(edict) ):
            entry = edict[i]
            for j in range(len(entry) ):
                for ek in entry[j].keys():
                    if ek == 'content':
                        for k in range(len(entry[j][ek]) ):
                            content = entry[j][ek][k]
                            for ck in content.keys():
                                if entry[j][ek][k][ck]:
                                    print('entry %d item %d %s %d %s %s' % (i,
                                        j, ek, k, ck, entry[j][ek][k][ck]) )
                    else:
                        if entry[j][ek]:
                            print('entry %d item %d %s %s' % (i, j, ek,
                                   entry[j][ek]) )


    def feed(self, rstr):
        xroot = ET.fromstring(rstr)
        for child in xroot:
            tag = child.tag
            taga = re.split('[{}]', child.tag)
            if len(taga) == 3:
                tag = taga[2]
            if tag == 'entry':
                stories = self.entry(child)
                self.adict['entries'].append(stories)
            else:
                self.adict[tag] = child.text
        print('atom feed number entries %d' % (len(self.adict['entries']) ),
              file=sys.stderr )
        return self.adict


def main():

    argp = argparse.ArgumentParser(description='parse rss or atom file')
    argp.add_argument('--atom', help='url of an atom file to parse')
    argp.add_argument('--rss', help='url of an rss file to parse')

    args = argp.parse_args()

    if args.rss:
        req = urllib.request.Request(args.rss)
        resp = urllib.request.urlopen(req)
        rstr = resp.read().decode('utf-8')
        mpr = _RSS()
        rdict = mpr.feed(rstr)
        mpr.reportrss(rdict)
        return

    if args.atom:
        req = urllib.request.Request(args.atom)
        resp = urllib.request.urlopen(req)
        rstr = resp.read().decode('utf-8')
        gna = _Atom()
        fdict = gna.feed(rstr)
        gna.reportatom()
        return

if __name__ == '__main__':
    main()


