from mako.template import Template
import sys
import os
import json
from pprint import pprint
SCHEMA_DIR = '/home/jkx/Devel/xaal_schemas/branches/schemas-0.7'
BLACK_LIST=['application-layer.cddl',
            'cache.basic.notice',
            'lamp.basic.notice',
            'lamp.color.notice',
            'lamp.dimmer.notice',
            'Makefile',
            'metadatadb.basic.notice',
            'powerrelay.basic.notice',
            'schema.cddl',
            'security-layer.cddl',
            'shutter.position.notice',
            'validate_schema',
]


def name_to_method(name):
    if name.endswith('.basic'):
        return name.split('.basic')[0]
    else:
        return name.replace('.','_')
    

def name_to_class(name):
    if name.endswith('.basic'):
        tmp = name.split('.basic')[0]
    else:
        tmp = name.replace('.','_')
    return tmp[0].upper() + tmp[1:]



def dump(jsonDict):
    print("=" * 80)
    keys = list(jsonDict.keys())
    keys.sort()
    for k in keys:
        if k in ["notifications","attributes","methods"]:
            print("====== %s ======= " % k)
        else:
            print("== %s => " % k,)
        pprint(jsonDict[k])


class Schemas:
    
    def __init__(self):
        self.__cache = {} 

    def load(self,filename):
        """ load schema from disk, and put it in cache
            return the file as dict"""
        if filename in self.__cache.keys():
            return self.__cache[filename]

        path = os.path.join(SCHEMA_DIR,filename)
        #print("Loading %s" % path)
        data = open(path,'r').read()
        jsonDict = json.loads(data)
        self.__cache.update({filename:jsonDict})
        return jsonDict

        
    def get_extends(self,name):
        """return the chain list off extends in reverse order, any.any is the first item"""
        current = name 

        extends = [name,]
        while 1:
            tmp = self.load(current)
            if "extends" in tmp.keys():
                current = tmp["extends"]
                extends.append(current)
            else:
                break
        extends.reverse()
        return extends


    def get(self,name):
        """return an complete schema w/ all extends included"""
        ext = self.get_extends(name)
        res = self.load(name)

        tmpMethods = {} 
        tmpAttr = {} 
        tmpNotifs = {}
        tmpDataModel = {}
        for e in ext:
            _dict = self.load(e)

            if "methods" in _dict.keys():
                tmp = _dict["methods"]
                tmpMethods.update(tmp)
                
            if "attributes" in _dict.keys():
                tmp = _dict["attributes"]
                tmpAttr.update(tmp)

            if "notifications" in _dict.keys():
                tmp = _dict["notifications"]
                tmpNotifs.update(tmp)

            if "datamodel" in _dict.keys():
                tmp = _dict["datamodel"]
                tmpDataModel.update(tmp)

        res["methods"] = tmpMethods
        res["attributes"] = tmpAttr
        res["notifications"] = tmpNotifs
        res["datamodel"] = tmpDataModel
        return res
        

    def get_devtypes(self):
        l = os.listdir(SCHEMA_DIR)
        r=[]
        for k in l:
            if k not in BLACK_LIST:
                r.append(k)
        r.sort()
        return r
            


class DeviceBuilder:
    def __init__(self):
        self.schemas = Schemas()
        self.basic = self.schemas.get('basic.basic')
        
    def is_basic_method(self,value):
        return value in self.basic['methods']
        
    def is_basic_attribute(self,value):
        return value in self.basic['attributes']

    def is_basic_notification(self,value):
        return value in self.basic['notifications']

    def is_basic_datamodel(self,value):
        return value in self.basic['datamodel']

    def get_schema(self,name):
        return self.schemas.get(name)

    def build(self,name,template):
        data = self.schemas.get(name)
        tmpl = Template(filename=template)

        attributes = {}
        for k in data['attributes']:
            if not self.is_basic_attribute(k):
                dict_ = data['attributes'][k]
                attributes.update({k:dict_})

        methods = {}
        for k in data['methods']:
            if not self.is_basic_method(k):
                dict_ = data['methods'][k]
                #print("%s: %s %s" % (k,dict_['description'],list(dict_['parameters'].keys())))
                methods.update({k:dict_})

        datamodel = {} 
        for k in data['datamodel']:
            if not self.is_basic_datamodel(k):
                dict_ = data['datamodel'][k]
                datamodel.update({k:dict_})
        
        args = {}
        args['name'] = name_to_method(name)
        args['Name'] = name_to_class(name)
        args['doc'] = data['description']
        args['devtype'] = name
        args['attributes'] = attributes
        args['methods'] = methods
        args['datamodel'] = datamodel
                
        print(tmpl.render(**args))
        #return args
                
    def build_all(self,template):
        devs = self.schemas.get_devtypes()
        for k in devs:
            self.build(k,template)
        
    def build_py(self):
        head = open('./head_py.txt','r').read()
        print(head)
        self.build_all('devices_py.mako')

    def build_js(self):
        head = open('./head_js.txt','r').read()
        print(head)
        self.build_all('devices_js.mako')

                
db = DeviceBuilder()
db.build_py()
#db.build_js()
