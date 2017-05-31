# -*- coding: utf-8 -*-
import sys, re, uuid
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import copy
from datetime import datetime



def removeColons(root):
    ns = {'ead':'urn:isbn:1-931666-22-9'}
    for el in root.iter('ead:*'):
        fack=el.attrib
        for x in fack:
            attrText = fack[x]
            if attrText.endswith(":"):
                fack[x] = attrText.replace(':','')
                # print(fack[x])

    return root

def updateValues(root):
    ns = {'ead':'urn:isbn:1-931666-22-9'}
    infile_path = sys.argv[1]

    time = datetime.now().strftime('%Y-%m-%d')
    #fix eadheader

    header=root.find('ead:eadheader',ns)

    header.set('findaidstatus','complete')
    # print(header.attrib)


    revision=SubElement(header, 'ead:revisiondesc')
    change=SubElement(revision,'ead:change')
    revDate=SubElement(change,'ead:date')
    revDate.set('normal', time)
    revDate.text = time
    item = SubElement(change, 'ead:item')
    item.text = 'This finding aid was updated to be more closely aligned with LC specifications using a python script created by Erik Radio.'

    #fix EADid
    EADid = header.find('ead:eadid',ns)
    EADid.text=infile_path.strip('.xml')





    #date

    pubDate = header.find('ead:filedesc/ead:publicationstmt/ead:date',ns)
    pubDate.text = pubDate.text.replace(u"© ","")

    #control access to remove list
    conAcc = root.find('ead:archdesc/ead:controlaccess',ns)
    # print(conAcc)
    subj=[]
    for thing in conAcc.findall('ead:list/ead:item/*',ns):
        subj.append(thing)
        # print(subj)
        for head in conAcc.findall('ead:head',ns):
            print(head.tag)
            conAcc.remove(head)
        for y in conAcc.findall('ead:list',ns):
            conAcc.remove(y)

    for x in subj:

        newsubj = SubElement(conAcc,x.tag)
        newsubj.text=x.text

    return root


def updateAttributes(root):
    ns = {'ead':'urn:isbn:1-931666-22-9'}
    header=root.find('ead:eadheader',ns)

    repoCode=root.find('ead:archdesc/ead:did/ead:unitid',ns)
    repoCode.set('repositorycode','US-azu')
    repoCode.set('countrycode','US')
    # print(repoCode.attrib)

    for repoDate in root.iter('ead:unitdate'):
        date=repoDate.attrib
        if date == '':
            date.attrib.pop('normal', None)
        if date == 'NaN':
            date.attrib.pop('normal', None)
        if date == 'AzU':
            date.attrib.pop('normal', None)
        # print(date)
    # print(repoDate)

    archDesc=root.find('ead:archdesc',ns)
    # print(archDesc)
    archDesc.attrib.pop('relatedencoding', None)
    archDesc.set('encodinganalog','351$c')

    #langmaterial
    langusage = header.find('ead:profiledesc/ead:langusage/ead:language',ns)
    langusage.set('langcode','eng')


    langusage2 = root.find('ead:archdesc/ead:did/ead:langmaterial/ead:language',ns)
    # print(langusage2)
    if langusage2 is not None:
        langusage2.attrib.pop('scriptcode', None)

    #remove all id attrib

    for x in root.iter('*'):
        name=x.get('id')
        if name is not None:
            x.attrib.pop('id', None)

    for el in root.iter('*'):
        fack=el.attrib
        for x in fack:
            attrText = fack[x]
            if attrText == '5441':
                fack[x] = attrText.replace('5441','544')
            if attrText == '544$1':
                fack[x] = attrText.replace('544$1','544')

    #add random ids to containers
    alldid = root.findall('.//ead:did',ns)
    for did in alldid:
        for elem in did.findall('./ead:container[1]',ns):
            randomID = uuid.uuid4()
            elem.set('id',str(randomID))
            newID=elem.get('id')
            for thing in did.findall('./ead:container',ns):
                if thing.get('id') == None:
                    thing.set('parent',newID)

    return root



def main():
    infile_path = sys.argv[1]
    outfile_path = 'rev_'+sys.argv[1]

    ns = {'ead':'urn:isbn:1-931666-22-9'}
    ET.register_namespace('ead',"urn:isbn:1-931666-22-9")

    tree=ET.parse(infile_path)
    root=tree.getroot()
    # print(root)
    updateValues(root)
    removeColons(root)
    updateAttributes(root)


    # print(tree)
    tree.write(outfile_path, xml_declaration=True,encoding='utf-8',method='xml')

# make this a safe-ish cli script
if __name__ == '__main__':
    # print(tree)

    main()
