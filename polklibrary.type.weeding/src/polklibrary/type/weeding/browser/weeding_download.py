from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent

import json, csv, io

class WeedListDownloadView(BrowserView):

    
    def __call__(self):    
        csv_data = self.build_csv()
        self.request.response.setHeader("Content-type", "application/csv")
        self.request.response.setHeader("Content-Disposition", "attachment;filename=" + self.context.id + '.csv');
        self.request.response.setBody(csv_data, lock=True)

        return self.request.response
        
    def build_csv(self):
        
        data = json.loads(self.context.json_db)
        
        outputstream = io.StringIO()
        writer = csv.writer(outputstream, delimiter=',', quotechar='"', dialect='excel')
        
        for row in data:
            writer.writerow(row[1::])
            
        output = outputstream.getvalue()
        outputstream.close()
        return output
        
        
    @property
    def portal(self):
        return api.portal.get()
        
        