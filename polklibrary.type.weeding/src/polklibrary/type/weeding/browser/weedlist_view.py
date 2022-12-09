from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent

import json, DateTime

class WeedListView(BrowserView):

    template = ViewPageTemplateFile("weedlist_view.pt")
    
    def __call__(self):    
        return self.template()


    @property
    def get_updated_last(self):
        return str(self.context.modified().strftime('%m/%d/%Y %H:%M:%S'))

    @property
    def get_headings(self):
        data = json.loads(self.context.json_db)
        return data[0]
    
    
    @property
    def is_editor(self):
        sm = getSecurityManager()
        if sm.checkPermission(ModifyPortalContent, self.context):
            return True
        return False

    @property
    def get_content(self):
        data = json.loads(self.context.json_db)
        return data[1:]
    
    
    @property
    def current_user_id(self):
        user = str(api.user.get_current())
        if user == "Anonymous User":
            return ''
        return user
        
    @property
    def portal(self):
        return api.portal.get()
        
        
class WeedListUpdate(BrowserView):

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
    
    
    
    
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        data = {
            'status':403,
            'message':'forbidden',
            'modified':'',
        }
        
        user_id = self.current_user_id
        if user_id != '':
            
            with api.env.adopt_roles(roles=['Manager']):
                user_email = user_id + '@uwosh.edu'
                row_id = int(self.request.form.get('id','-1'))
                data['status'] = 200
                if self.request.form.get('action','').lower() == 'add':
                    #print("add")
                    data['message'] = 'Added'
                    jdb = json.loads(self.context.json_db)
                    for row in jdb:
                        if row[0] == row_id:
                            row[1] = row[1] + user_email+','
                            break
                    self.context.json_db = json.dumps(jdb)
                elif self.request.form.get('action','').lower() == 'remove':
                    #print("remove")
                    data['message'] = 'Removed'    
                    jdb = json.loads(self.context.json_db)
                    for row in jdb:
                        if row[0] == row_id:
                            row[1] = row[1].replace(user_email+',','')
                            break
                    self.context.json_db = json.dumps(jdb)
                
                self.context.setModificationDate(DateTime.DateTime())
                self.context.reindexObject(idxs=['modified'])

        
        data['modified'] = str(self.context.modified().strftime('%m/%d/%Y %H:%M:%S'))
        return json.dumps(data)

    @property
    def current_user_id(self):
        user = str(api.user.get_current())
        if user == "Anonymous User":
            return ''
        return user
        
    
    
    @property
    def portal(self):
        return api.portal.get()
        
        