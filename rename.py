#!/usr/bin/env python

import argparse
import os
import shutil, errno
import re
import json

def process_params():
    parser = argparse.ArgumentParser(description='Rename an icon downloaded from design.google.com/icons/')
    parser.add_argument('--currentIconName', dest='oldName', required=True, help='the current icon name (without the style or size suffixes)')
    parser.add_argument('--newIconName', dest='newName', required=True, help='the new name for the icon')
    parser.add_argument('--no-style', dest='removeStyle', action='store_true', help='set true if you want to remove the style suffix (_black or _white)')
    parser.add_argument('--no-size', dest='removeSize', action='store_true', help='set true if you want to remove the size suffix (_18dp, _24dp etc)')

    parser.set_defaults(removeStyle=False)
    parser.set_defaults(removeSize=False)

    return parser.parse_args()


def base_new_name(folder):
    newName = params.newName

    oldLen = len(params.oldName)

    styleFinalPos = folder.index("_", oldLen + 1)
    styleText = folder[oldLen:styleFinalPos]
    sizeText = folder[styleFinalPos:]

    if not params.removeStyle:
        newName = newName + styleText

    if not params.removeSize:
        newName = newName + sizeText

    return newName


def full_new_name(old, new):
    oldExtPos = old.rindex(".")

    multiplierSuffix = re.search(r"(_[0-9]{1,2}x)", old)
    if multiplierSuffix:
        new += multiplierSuffix.group(0)

    new += old[oldExtPos:]

    return new


def rename_file(old, new):
    os.rename(old, full_new_name(old, new))


def rename_android(folder, newName):
    path = folder + "/android/"
    for drawableFolder in [a for a in os.listdir(path) if a.startswith("drawable-")]:
        base = path + drawableFolder + "/"
        rename_file(base + os.listdir(base)[0], base + newName)


def fix_ios_contents_json(filePath, newName):
    with open(filePath) as data_file:
        data = json.load(data_file)

    for imageData in data["images"]:
        imageData["filename"] = full_new_name(imageData["filename"], newName)

    with open(filePath, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))


def rename_ios(folder, newName):
    path = folder + "/ios/"
    for imageset in os.listdir(path):
        imagesetPath = path + imageset + "/"
        for file in os.listdir(imagesetPath):
            if file != "Contents.json":
                rename_file(imagesetPath + file, imagesetPath + newName)

            else:
                fix_ios_contents_json(imagesetPath + file, newName)

        rename_file(imagesetPath, path + newName)



def rename_web(folder, newName):
    path = folder + "/web/"
    for image in os.listdir(path):
        rename_file(path + image, path + newName)


def rename_icon_folder(folder):
    newFolder = params.newName + folder[len(params.oldName):]
    shutil.copytree(folder, newFolder)

    newName = base_new_name(folder)

    rename_android(newFolder, newName)
    rename_ios(newFolder, newName)
    rename_web(newFolder, newName)

    # uncomment during test
    # shutil.rmtree(newFolder)

params = process_params()

baseFolderName = params.oldName
iconsFolders = [folder for folder in os.listdir(".") if folder.startswith(params.oldName)]
for folder in iconsFolders:
    rename_icon_folder(folder)
