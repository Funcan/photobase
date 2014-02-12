#!/usr/bin/env python

from __future__ import print_function

import os
from os import listdir
from os.path import isfile, isdir
import logging as log

import magic
import stat

PHOTOPATHROOT = "/media/bc0e8b11-d46e-4710-b8c4-057884fe8d1a/home photo backup"

class Spider(object):
    """
    Spider a filesystem, applying a set of actions at various nodes
    """
    def __init__(self, root):
        self.files = []
        self.folders = []

    def file_count(self):
        """
        Return the number of files encountered
        """
        return len(self.files)

    def visit_dir(self, directory):
        """
        Called for every directory found
        """
        pass

    def visit_file(self, filename):
        """
        Called for every normal file found
        """
        print("Found file %s" % filename)

    def spider(self, root):
        """
        Start spidering from the path 'root'
        """
        contents = listdir(root)
        log.debug("visiting path %s found %d entries", root, len(contents))
        for entry in contents:
            entry = os.path.join(root, entry)
            if isfile(entry):
                self.files.append(entry)
                self.visit_file(entry)
            elif isdir(entry):
                self.folders.append(entry)
                self.visit_dir(entry)
                self.spider(entry)
            else:
                log.error("Don't know how to process %s", entry)

class PhotoSpider(Spider):
    """
    Spider that understands image files and stores useful details
    of them in a database
    """
    def __init__(self, root):
        Spider.__init__(self, root)
        self.identifier = magic.open(magic.MAGIC_NONE)
        self.identifier.load()

    def visit_file(self, filename):
        log.info("Processing %s", filename)
        record = {}

        filetype = self.identifier.file(filename)
        record["file type"] = filetype
        record["file size"] = os.stat(filename)[stat.ST_SIZE]

        if filetype.startswith("JPEG"):
            record.update(self.handle_jpeg(filename))
        else:
            log.warning("Don't know how to handle type: %s", filetype)
        log.info("Recording %s", record)

    def handle_jpeg(self, filename):
        """
        Grab data from a JPEG file, return a dict
        """
        log.debug("Processing JPEG file: %s", filename)
        record = {}
        record["file type"] = "JPEG"
        return record


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)

    spider = PhotoSpider(PHOTOPATHROOT)
    spider.spider(PHOTOPATHROOT)
    log.info("%d files processed", spider.file_count())
