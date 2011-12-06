from zope import component
from zope.app.component.interfaces import ISite
import zope.event

from Products.CMFCore.utils import getToolByName
from Products.Five.component import disableSite
from five.localsitemanager import make_objectmanager_site

from p4a.subtyper.interfaces import ISubtypeAddedEvent
from p4a.subtyper.interfaces import ISubtypeRemovedEvent

from collective.lineage.interfaces import IChildSite
from collective.lineage.events import ChildSiteCreatedEvent
from collective.lineage.events import ChildSiteRemovedEvent

def reindexObjectProvides(folder):
    pc = getToolByName(folder, 'portal_catalog')
    pc.reindexObject(
        folder,
        idxs=['object_provides']
    )

def enableFolder(folder):
    if not ISite.providedBy(folder):
        make_objectmanager_site(folder)
    # reindex so that the object_provides index is aware of our
    # new interface
    reindexObjectProvides(folder)
    zope.event.notify(ChildSiteCreatedEvent(folder))

def disableFolder(folder):
    # remove local site components
    disableSite(folder)

    # reindex the object so that the object_provides index is
    # aware that we've removed it
    reindexObjectProvides(folder)
    zope.event.notify(ChildSiteRemovedEvent(folder))

@component.adapter(IChildSite, ISubtypeAddedEvent)
def enableChildSite(object, event):
    """When a lineage folder is created, turn it into a component site
    """
    folder = event.object
    enableFolder(folder)

@component.adapter(IChildSite, ISubtypeRemovedEvent)
def disableChildSite(object, event):
    """When a child site is turned off, remove the local components
    """
    if event.subtype is not None:
        folder = event.object
        disableFolder(folder)
