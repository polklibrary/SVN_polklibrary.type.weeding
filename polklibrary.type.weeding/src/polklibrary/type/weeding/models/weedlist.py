from plone import api
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.browser.add import  DefaultAddForm, DefaultAddView
from plone.dexterity.browser.edit import DefaultEditForm

import csv, io, re, ast, json

override_choices = SimpleVocabulary([
    SimpleTerm(value=u'nothing', title=u'Do nothing'),
    SimpleTerm(value=u'overlay', title=u'Update content but keep user data'),
    SimpleTerm(value=u'fresh', title=u'Use fresh data from CSV, no user data kept'),
])


class IWeedList(model.Schema):

    title = schema.TextLine(
            title=u"Weeding Range/Title",
            required=True,
        )
        
    backpath = schema.TextLine(
            title=u"Back",
            required=False,
            default=u"../"
        )
        
    # body = RichText(
            # title=u"Information",
            # default_mime_type='text/structured',
            # required=False,
            # default=u"",
        # )
        
    file = NamedBlobFile(
            title=u"CSV Weed List File (see overwrite below)",  
            description=u"",
            required=False
        )
        

    override_db = schema.Choice(
        title=u"Override the JSON Database?",
        source=override_choices,
        required=True,
    )
        
    json_db = schema.Text(
            title=u"JSON Database",
            description=u"DO NOT EDIT!",
            required=False
        )


class AddForm(DefaultAddForm):
    portal_type = 'polklibrary.type.weeding.models.weedlist'

    def add(self, obj):
        DefaultAddForm.add(self, obj)
        #print("ADD POST RUN")
        
        sio = io.StringIO(obj.file.data.decode("utf-8-sig"))
        reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel)
        data = []
        index = 0
        for row in reader:
        
            # setup user column
            if index == 0:
                clean_row = ['ID','Users']
            else:
                clean_row = [index, '']
                
            for item in row:
                clean_row.append(item.strip()) # clean up
            data.append(clean_row)
            index+=1
    
        json_data = json.dumps(data)
        
        obj.json_db = json_data        
        return obj
    
    
class AddView(DefaultAddView):
    form = AddForm


class EditForm(DefaultEditForm):
    portal_type = 'polklibrary.type.weeding.models.weedlist'


    def update(self):
        DefaultEditForm.update(self)
        
        if self.request.form.get('form.buttons.save', ''):
        
            #print("EDIT POST RUN")
            if self.context.override_db == u'fresh':
                #print("YES, FRESH DB!")
                sio = io.StringIO(self.context.file.data.decode("utf-8-sig"))
                reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel)
                data = []
                index = 0
                for row in reader:
                    # setup user column
                    if index == 0:
                        clean_row = ['ID','Users']
                    else:
                        clean_row = [index, '']
                        
                    for item in row:
                        clean_row.append(item.strip()) # clean up
                    data.append(clean_row)
                    index+=1
            
                json_data = json.dumps(data)
                self.context.override_db = u'nothing'
                self.context.json_db = json_data
                
                
            if self.context.override_db == u'overlay':
                #print("YES, OVERLAY DB!")
                
                # NEW DATA START
                sio = io.StringIO(self.context.file.data.decode("utf-8-sig"))
                reader = csv.reader(sio, delimiter=',', quotechar='"', dialect=csv.excel)
                data = []
                index = 0
                for row in reader:
                    # setup user column
                    if index == 0:
                        clean_row = ['ID','Users']
                    else:
                        clean_row = [index, '']
                        
                    for item in row:
                        clean_row.append(item.strip()) # clean up
                    data.append(clean_row)
                    index+=1
                # NEW DATA END
            
            
                # GET MATCH POINTS
                old_data = json.loads(self.context.json_db)   
                
                old_data_pcn = 0
                i = 0
                for item in old_data[0]:
                    if 'permanent call number' in item.lower():
                        old_data_pcn = i
                    i+=1
                
                new_data_pcn = 0
                i = 0
                for item in data[0]:
                    if 'permanent call number' in item.lower():
                        new_data_pcn = i
                    i+=1
                
                #print ('Old CN: ' + str(old_data_pcn))
                #print ('New CN: ' + str(new_data_pcn))
                # END GET MATCH POINTS
                
                # merge
                for row in data:
                    for old_row in old_data:
                        if old_row[old_data_pcn] == row[new_data_pcn]:
                            row[1] = old_row[1] 
                            break
                    
                json_data = json.dumps(data)
                self.context.override_db = u'nothing'
                self.context.json_db = json_data
                
            else:
                pass
                #print("NOTHING, OVERRIDING DB!")