import numpy as np
import threading
import matplotlib
from matplotlib.lines import Line2D
from matplotlib.artist import Artist 
from matplotlib.backend_tools import ToolBase
from matplotlib.patches import Polygon, Rectangle
from matplotlib.widgets import Cursor
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg
from lxml import etree as ET 
import tkinter as tk 
from tkinter import ttk, messagebox
 

 

class Editor ():

    def __init__(self): 
        matplotlib.use('TkAgg')
        self.clickX = None
        self.clickY = None
        self.releaseX  = None
        self.releaseY = None
        self.onClick = False  
        self.imageIndex = 0  
        self.onRelease = False
        self.boxType = None
        self.boxTriggered = False
        self.zoomTriggered = False
        self.ImageFolderPath = None
        self.pageFolderPath = None   
        self.unsavedChanges = False
        
        
        ''' zoom and resolution '''
        self.imageXMax= 0
        self.imageYMax = 0
        self.xMin = 0
        self.xMax = 0
        self.yMin = 0
        self.yMax = 0
        self.zoomFactor = 1.25
        
        self.simpleChoixBox = SimpleChoiceBox()  
        ''' plot, ax, figure '''
        plt.rcParams['image.cmap'] = 'gray'
        plt.rcParams['toolbar'] = 'toolmanager'   
        self.fig, self.ax = plt.subplots() 
        self.fig.canvas.set_window_title('METS - Image anotation') 
        self.ax.polygonInteractorList = []
        self.ax.editor = self 
        
        ''' dictionaries'''
        self.fcDictionary= {"paragraph": (0.00,0.50,0.74,0.2), 
                            "heading": (0.85,0.32,0.09,0.2), 
                            "caption": (0.92,0.69,0.12,0.2), 
                            "header": (0.49,0.18,0.55,0.2),
                            "footer": (0.46,0.67,0.19,0.2),
                            "drop-capital": (0.30,0.75,0.93,0.2),
                            "marginalia": (0.64,0.08,0.18,0.2),
                            "footnote": (0,1,0,0.2), 
                            "staffNotation": (0.00,0.50,0.74,0.2), 
                            "tablatureNotation": (0.85,0.32,0.09,0.2), 
                            "table": (0.92,0.69,0.12,0.2), 
                            "graphic": (0.49,0.18,0.55,0.2),
                            "image": (0.46,0.67,0.19,0.2),
                            "linedrawing": (0.30,0.75,0.93,0.2), 
                            "separator": (0,1,0,0.2),
                            "other": (0,1,0,0.2) 
                            }
        self.regionDictionary = []
        
        for element in self.fcDictionary:
            self.regionDictionary.append(element) 
        
        
        
        ''' events '''
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease) 
        self.fig.canvas.mpl_connect('motion_notify_event', self.motion) 
        self.fig.canvas.mpl_connect('pick_event', self.onpick) # Activate the object's method
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
         
        ''' tools and buttons '''
        self.toolmanager = self.fig.canvas.manager.toolmanager
        
        
        ''' save, open....'''
        self.toolmanager.add_tool('Open', self.OpenBox, gid='saveOpen') 
        self.toolmanager.add_tool('Save', self.SaveBox, gid='saveOpen') 
        self.toolmanager.add_tool('Previous', self.Previous, gid='saveOpen') 
        self.toolmanager.add_tool('Next', self.Next, gid='saveOpen') 
        
        ''' 1. text regions '''
        self.toolmanager.add_tool('Paragraph', self.ParagraphBox, gid='textAreaGroup') 
        self.toolmanager.add_tool('Heading', self.HeadingBox, gid='textAreaGroup')
        self.toolmanager.add_tool('Caption', self.CaptionBox, gid='textAreaGroup')
        self.toolmanager.add_tool('Header', self.HeaderBox, gid='textAreaGroup')
        self.toolmanager.add_tool('Footer', self.FooterBox, gid='textAreaGroup')
        self.toolmanager.add_tool('Drop-capital', self.DropCapitalBox, gid='textAreaGroup')
        self.toolmanager.add_tool('Marginalia', self.MarginaliaBox, gid='textAreaGroup')
        self.toolmanager.add_tool('Footnote', self.FootnoteBox, gid='textAreaGroup')
        
        ''' 2. Music regions '''
        self.toolmanager.add_tool('Staff notation', self.StaffNotationBox, gid='musicAreaGroup')
        self.toolmanager.add_tool('Tablature notation', self.TablatureNotationBox, gid='musicAreaGroup')
        
        ''' 3. Image, tables, and separator regions '''
        self.toolmanager.add_tool('Table', self.TableBox, gid='imageGroup')
        self.toolmanager.add_tool('Graphic', self.GraphicBox, gid='imageGroup')
        self.toolmanager.add_tool('Image', self.ImageBox, gid='imageGroup')
        self.toolmanager.add_tool('Line drawing', self.LineDrawingBox, gid='imageGroup')
        self.toolmanager.add_tool('Separator', self.LineDrawingBox, gid='imageGroup')
    
        ''' 4. else '''
        self.toolmanager.add_tool('Other', self.OtherBox, gid='textAreaGroup') 
        self.toolmanager.add_tool('Delete box', self.DeleteBox, gid='deleteBoxGroup') 
        
    
        
         
        ''' add everything to toolbar '''
        self.fig.canvas.manager.toolmanager.remove_tool('home') 
        self.fig.canvas.manager.toolmanager.remove_tool('forward') 
        self.fig.canvas.manager.toolmanager.remove_tool('back') 
        self.fig.canvas.manager.toolmanager.remove_tool('save') 
        self.fig.canvas.manager.toolmanager.remove_tool('pan') 
        self.fig.canvas.manager.toolmanager.remove_tool('zoom') 
        self.fig.canvas.manager.toolmanager.remove_tool('help') 
        self.fig.canvas.manager.toolmanager.remove_tool('subplots')  
        
        
        
        self.fig.canvas.manager.toolbar.add_tool('Open', '', 1) 
        self.fig.canvas.manager.toolbar.add_tool('Save', '', 1) 
        self.fig.canvas.manager.toolbar.add_tool('Previous', '', 1) 
        self.fig.canvas.manager.toolbar.add_tool('Next', '', 1) 
        
        self.fig.canvas.manager.toolbar.add_tool('Paragraph', '', 1) 
        self.fig.canvas.manager.toolbar.add_tool('Heading', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Caption', '', 1)   
        self.fig.canvas.manager.toolbar.add_tool('Header', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Footer', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Drop-capital', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Marginalia', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Footnote', '', 1)
        
        self.fig.canvas.manager.toolbar.add_tool('Staff notation', '', 1) 
        self.fig.canvas.manager.toolbar.add_tool('Tablature notation', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Table', '', 1)   
        self.fig.canvas.manager.toolbar.add_tool('Graphic', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Image', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Line drawing', '', 1)
        self.fig.canvas.manager.toolbar.add_tool('Other', '', 1) 
          
        ''' maximise '''
        if callable(plt.get_current_fig_manager):
            figManager = plt.get_current_fig_manager()
            if callable (figManager.full_screen_toggle): figManager.full_screen_toggle()
        
        ''' show plot '''
        plt.show()  
        
        
    def addPolyGon (self, xyArray): 
        
        ''' make sure that coordinates imply a surface and do not correspond to as single point '''
        isSurface = False
        firstX= xyArray[0][0]
        firstY= xyArray[0][1]
        for coordinates in xyArray:
            if coordinates [0] != firstX or coordinates [1] != firstY: 
                isSurface = True
                break
        if isSurface == False:  
            self.ax.figure.canvas.draw_idle() 
            return
            
                
        
        polygon = self.createPolygon(self.boxType, xyArray)
        self.ax.add_patch(polygon) 
        textRegion = TextRegion(
            xyArray,
            "region_"+ str(len (self.ax.polygonInteractorList)),
            len(self.ax.polygonInteractorList),
            None,
            None)
        textRegion.regionName=self.boxType
        
        self.ax.polygonInteractorList.append(PolygonInteractor(self.ax, polygon, textRegion))
        self.unsaved()
    
    def createPolygon (self, regionName, xyArray):
        if regionName == "paragraph":
                polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["paragraph"], ec=(0,0,0,1), picker=5)      
        elif regionName == "heading":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["heading"], ec=(0,0,0,1), picker=5)
        elif regionName == "caption":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["caption"], ec=(0,0,0,1), picker=5) 
        elif regionName == "header":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["header"], ec=(0,0,0,1), picker=5)
        elif regionName == "footer":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["footer"], ec=(0,0,0,1), picker=5)
        elif regionName == "drop-capital":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["drop-capital"], ec=(0,0,0,1), picker=5)
        elif regionName == "marginalia":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["marginalia"], ec=(0,0,0,1), picker=5)
        elif regionName == "footnote":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["footnote"], ec=(0,0,0,1), picker=5)
        elif regionName == "staffNotation":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["staffNotation"], ec=(0,0,0,1), picker=5)
        elif regionName == "tablatureNotation":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["tablatureNotation"], ec=(0,0,0,1), picker=5)
        elif regionName == "table":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["table"], ec=(0,0,0,1), picker=5)
        elif regionName == "graphic":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["graphic"], ec=(0,0,0,1), picker=5)
        elif regionName == "image":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["image"], ec=(0,0,0,1), picker=5)
        elif regionName == "linedrawing":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["linedrawing"], ec=(0,0,0,1), picker=5) 
        elif regionName == "separator":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["linedrawing"], ec=(0,0,0,1), picker=5) 
        elif regionName == "separator":
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["separator"], ec=(0,0,0,1), picker=5) 
        else:  
            polygon = Polygon(xyArray, animated=False, fc=self.fcDictionary["other"], ec=(0,0,0,1), picker=5)
        polygon.regionName = regionName 
        return polygon    
    
    def loadImage (self, imgPath):
        image = mpimg.imread(imgPath)
        self.imageXMax = image.shape[0]
        self.imageYMax = image.shape[1]
        self.xMax = self.imageXMax
        self.yMax = self.imageYMax 
        self.im = self.ax.imshow(image)
        
    def loadPage (self, pageIndex):
        self.ax.axes.clear()  
        
        ''' delet ols polygon interactors if any '''
        for polygonInteractor in self.ax.polygonInteractorList:  
            polygonInteractor.clearCoordinates() 
            del polygonInteractor 
        self.ax.polygonInteractorList.clear() 
        
        
        ''' read page '''
        self.pageXMLPath = self.projectFilePath+self.pageFileList[pageIndex]
        self.pageXML = ReadWritePageXML(self.pageXMLPath)
        self.imgPath = self.projectFilePath + self.pageXML.getImagePath()
        textRegionList = self.pageXML.readPageRegionXML() 
        self.pageTitle = self.pageXMLPath.split("/")[-1]
        self.ax.set_title(self.pageTitle) 
        self.loadImage(self.imgPath) 
        self.loadPolygons(textRegionList) 
        
        
        ''' set annotation display '''
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False) 
        
        ''' redraw if necessary '''
        self.ax.figure.canvas.draw_idle() 
        
    def loadPolygons(self, textRegionList):  
        for textRegion in textRegionList:
            xyArray = np.array(textRegion.coordinates)
            polygon = self.createPolygon(textRegion.regionName, xyArray)
            self.ax.add_patch(polygon) 
            self.ax.polygonInteractorList.append(PolygonInteractor(self.ax,polygon, textRegion)) 
    
    def motion (self, event):   
        if hasattr(self, 'annot._visible') and self.annot._visible == True:
            self.annot.set_visible(False) 
            self.fig.canvas.draw_idle() 
        
        if self.boxTriggered == True and self.onClick == True:
            self.rect.set_x(self.clickX) 
            self.rect.set_y(self.clickY)
            
            self.rect.set_width(event.xdata-self.clickX)
            self.rect.set_height(event.ydata-self.clickY)
            
        if self.zoomTriggered == True and self.onClick == True: 
            self.rect.set_x(self.zoomXMinCoord) 
            self.rect.set_y(self.zoomYMinCoord)
            
            self.rect.set_width(event.xdata-self.zoomXMinCoord)
            self.rect.set_height(event.ydata-self.zoomYMinCoord)     
    
    def nextPage (self):
        
        if self.imageIndex < (len (self.pageFileList)-1): 
            if self.unsavedChanges: 
                if messagebox.askyesno("Question","Save changes ?") == True: self.save()
            self.imageIndex = self.imageIndex+1
            self.loadPage(self.imageIndex) 
            
    def on_key(self, event):   
        if event.key == "backspace": ### remove polygons  
            for polygonInteractor in self.ax.polygonInteractorList:
                if polygonInteractor.showverts == True: 
                    polygonInteractor.clearCoordinates() 
                    self.ax.polygonInteractorList.remove(polygonInteractor)
                    del polygonInteractor    
                    self.unsaved()
                    self.ax.figure.canvas.draw_idle()  
                    
        elif event.key in ["P", "H", "C", "ctrl+h", "F", "D", "M", "F", "O", "S", "T", "ctrl+t", "G", "I", "ctrl+l"] :
       
            self.ax.editor.boxTriggered = True
            self.ax.editor.setCursor()   
            if event.key == "P": self.ax.editor.boxType = "paragraph"
            elif event.key == "H": self.ax.editor.boxType = "heading"
            elif event.key == "C": self.ax.editor.boxType = "caption"
            elif event.key == "ctrl+h": self.ax.editor.boxType = "header"
            elif event.key == "F": self.ax.editor.boxType = "footer"
            elif event.key == "D": self.ax.editor.boxType = "drop-capital"
            elif event.key == "M": self.ax.editor.boxType = "marginalia"
            elif event.key == "F": self.ax.editor.boxType = "footnote"
            elif event.key == "O": self.ax.editor.boxType = "other"
            
            elif event.key == "S": self.ax.editor.boxType = "staffNotation"
            elif event.key == "ctrl+s": self.ax.editor.boxType = "separator"
            elif event.key == "T": self.ax.editor.boxType = "tablatureNotation"
            elif event.key == "ctrl+t": self.ax.editor.boxType = "table"
            elif event.key == "G": self.ax.editor.boxType = "graphic"
            elif event.key == "I": self.ax.editor.boxType = "image"
            elif event.key == "ctrl+l": self.ax.editor.boxType = "linedrawing"   
        elif event.key == "super+s": self.save() 
        elif event.key == "super+o": self.openFile()  
        elif event.key == "left": self.previousPage()
        elif event.key == "right": self.nextPage() 
        elif event.key =="+":  
            for polygonInter in self.ax.polygonInteractorList: 
                if polygonInter.showverts == True:   
                    thread = threading.Thread( target=self.simpleChoixBox.SimpleChoiceBox(self.regionDictionary, polygonInter))
                    thread.start() 
                    # wait here for the result to be available before continuing
                    thread.join() 
                    thread._stop()
        
                    polygonInter.ocrRegion.regionName=self.simpleChoixBox.polygonType
                    polygonInter.ocrRegion.index=self.simpleChoixBox.polygonOrder
                    polygonInter.poly.set_facecolor(self.fcDictionary[polygonInter.ocrRegion.regionName]) 
                    polygonInter.poly.type = self.simpleChoixBox.polygonType
                    self.fig.canvas.draw_idle()  
                    self.unsaved()
                    
    def onclick(self, event):              
        self.onClick = True
        self.onRelease = False   
        if self.boxTriggered == True :
            self.clickX = event.xdata
            self.clickY = event.ydata 
            self.rect = Rectangle((self.clickX,self.clickY),3,3,linewidth=1,edgecolor='r',facecolor='none')  
            self.ax.add_patch(self.rect)  
        elif event.button==3: # display polygon information
            
                if event.inaxes == self.ax: 
                    for polygonInter in self.ax.polygonInteractorList:
                        cont, ind = polygonInter.poly.contains(event)
                        if cont: 
                            self.update_annot(polygonInter) 
                            self.annot.set_visible(True)
                            self.fig.canvas.draw_idle()  
        elif event.key=="shift": # zoom 
            self.cursor = Cursor(self.ax, useblit=False, color='black', linewidth=1)
            self.ax.figure.canvas.draw_idle()
            self.zoomTriggered = True
            self.zoomXMinCoord = event.xdata
            self.zoomYMinCoord = event.ydata
            self.rect = Rectangle((self.zoomXMinCoord,self.zoomYMinCoord),3,3,linewidth=1,edgecolor='r',facecolor='none')  
            self.ax.add_patch(self.rect)  
        elif event.key =="control": ## original size
            self.xMax = self.imageXMax
            self.yMax = self.imageYMax
            self.xMin = 0
            self.yMin = 0 
            plt.axis([0,self.imageYMax,self.imageXMax,0])
            self.ax.figure.canvas.draw_idle() 
            
    def onpick (self,event): 
        self.ax.figure.canvas.draw_idle()
        for polyInteractor in self.ax.polygonInteractorList:
            polyInteractor.showverts = False
            polyInteractor.line.set_visible(polyInteractor.showverts) 
            if polyInteractor.poly == event.artist:
                polyInteractor.showverts = True
                polyInteractor.line.set_visible(polyInteractor.showverts)  
                
    def onrelease (self, event):
        self.onClick = False
        self.onRelease = True
        if self.boxTriggered == True:
            
            self.releaseX = event.xdata
            self.releaseY = event.ydata
            xyArray = np.array([[self.clickX,self.clickY],[self.clickX,self.releaseY],[self.releaseX,self.releaseY],[self.releaseX,self.clickY]])
            xyArray = xyArray.astype(int) 
            self.addPolyGon(xyArray)
            self.boxTriggered= False 
            self.cursor.lineh.set_linewidth(0)
            self.cursor.linev.set_linewidth(0)
            del self.cursor 
            self.rect.remove() 
        if self.zoomTriggered: 
            self.zoomTriggered= False
            self.zoomXMaxCoord = event.xdata
            self.zoomYMaxCoord = event.ydata
            self.cursor.lineh.set_linewidth(0)
            self.cursor.linev.set_linewidth(0)
            del self.cursor 
            self.rect.remove()  
            plt.axis([self.zoomXMinCoord,self.zoomXMaxCoord,self.zoomYMaxCoord, self.zoomYMinCoord]) 
            self.ax.figure.canvas.draw_idle()   
            
    def openFile(self): 
        if self.unsavedChanges: self.save()
        self.imageIndex = 0
       
        filename = tk.filedialog.askopenfilename()

        ''' read METS '''
        self.metsXmlPath=filename
        self.projectFilePath = self.metsXmlPath.replace("mets.xml", "") 
        self.metsData = ReadWriteMets(self.metsXmlPath)
        self.pageFileList = self.metsData.getFileGroup()
        
        ''' load first page '''
        self.loadPage(self.imageIndex) 
   
    def previousPage(self): 
        if self.imageIndex > (0):
            if self.unsavedChanges: 
                if messagebox.askyesno("Question","Save changes ?") == True: self.save()
            self.imageIndex = self.imageIndex-1
            self.loadPage(self.imageIndex)
            
    def save(self): 
        self.ax.editor.updateRegionData()
        self.ax.editor.pageXML.writePageRegionXML(self.ax.polygonInteractorList) 
        self.unsaved(False)
        self.fig.canvas.draw_idle()
    
    def setCursor (self):
        for polyInteractor in self.ax.polygonInteractorList:
            polyInteractor.showverts = False
            polyInteractor.line.set_visible(polyInteractor.showverts)
        self.cursor = Cursor(self.ax, useblit=False, color='black', linewidth=1) 
    
    def unsaved (self, isUnsaved= True):
        if isUnsaved:
            self.unsavedChanges = True
            self.ax.set_title(self.pageTitle + "*") 
        else: 
            self.unsavedChanges = False
            self.ax.set_title(self.pageTitle) 
                
    def update_annot(self, polygonInter):

        self.annot.xy = polygonInter.poly.centerCoordinates  
        text = "#" + str(polygonInter.ocrRegion.index) + ": " + polygonInter.ocrRegion.regionName
        self.annot.set_text(text) 
        self.annot.get_bbox_patch().set_alpha(1)
    
    def updateRegionData (self):
        
        ''' make sure that all interactors with 0 coordinates are deleted ''' 
        temporaryList = []
        for polyInt in self.ax.polygonInteractorList:
            isNullCoordinates = True
            for coordinates in (polyInt.poly.xy): 
                for coordinate in coordinates:
                    if coordinate != 0: 
                        temporaryList.append(polyInt)
                        isNullCoordinates = False 
                        break
                if isNullCoordinates == False: break
        self.ax.polygonInteractorList = temporaryList
        ''' make sure that all interactors with 0 coordinates are deleted ''' 
        
        
        
        
        ''' update region indices '''
        for polyInt in self.ax.polygonInteractorList: polyInt.ocrRegion.index =  polyInt.ocrRegion.index
        
        self.ax.polygonInteractorList= sorted(self.ax.polygonInteractorList, key=lambda polygonInter: polygonInter.ocrRegion.index)
        
        ''' used to check region data and to complete it if necessary '''
        for counter, polygonInteractor in enumerate(self.ax.polygonInteractorList):
            region = polygonInteractor.ocrRegion
            
            ''' complete region id '''
            region.index = counter
            region.id = "region_id_" + str(region.index)
            
            ''' complete region class, custom, type according  '''
            if region.regionName in ["paragraph", "heading", "caption", "header", "footer", "drop-capital", "marginalia", "footnote", "other"]:
                region.regionClass = "TextRegion" 
                region.type = region.regionName
                
            elif region.regionName in ["staffNotation", "tablatureNotation"]:
                region.regionClass = "MusicRegion" 
                region.custom = region.regionName
                region.type = None
                
            elif region.regionName in ["table", "graphic", "image", "linedrawing", "separator"]:
                region.custom = None
                region.type = None
                if region.regionName == "table": region.regionClass = "TableRegion"  
                elif region.regionName == "graphic": region.regionClass = "GraphicRegion"  
                elif region.regionName == "image": region.regionClass = "ImageRegion"  
                elif region.regionName == "linedrawing": region.regionClass = "LineDrawingRegion"  
                elif region.regionName == "separator": region.regionClass = "SeparatorRegion"  
            region.coordinates = polygonInteractor.poly.xy.round() 
            region.coordinates = region.coordinates.astype(int)   
            
            
    class CaptionBox(ToolBase):
        default_keymap = ''
        description = 'Identify a caption'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "caption"
            self.ax.editor.setCursor()
            
    class DeleteBox (ToolBase):
        default_keymap = ''
        description = 'Delete a box'
        def __init__(self, *args, gid, **kwargs):
            self.triggered = False
            self.ax = args[0].figure.axes[0]
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):            
            self.triggered = True 
            ''' remove polygonselections '''  
            for polygonInteractor in self.ax.polygonInteractorList:
                if polygonInteractor.showverts == True: 
                    polygonInteractor.clearCoordinates()
                    del polygonInteractor 
                    
                    self.ax.figure.canvas.draw_idle() 
                    
    class DropCapitalBox(ToolBase):
        default_keymap = ''
        description = 'Identify a drop-capital'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "drop-capital"
            self.ax.editor.setCursor()
            
    class FooterBox(ToolBase):
        default_keymap = ''
        description = 'Identify a footer'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "footer"
            self.ax.editor.setCursor()
            
    class FootnoteBox(ToolBase):
        default_keymap = ''
        description = 'Identify a footnote'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "footnote"
            self.ax.editor.setCursor()
            
    class GraphicBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "graphic"
            self.ax.editor.setCursor()
            
    class HeaderBox(ToolBase):
        default_keymap = ''
        description = 'Identify a header'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "header"
            self.ax.editor.setCursor()
            
    class HeadingBox(ToolBase):
        default_keymap = ''
        description = 'Identify a heading'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "heading"
            self.ax.editor.setCursor()
            
    class ImageBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "image"
            self.ax.editor.setCursor() 
            
    class LineDrawingBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "linedrawing"
            self.ax.editor.setCursor()
            
    class MarginaliaBox(ToolBase):
        default_keymap = ''
        description = 'Identify marginalia'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "marginalia"
            self.ax.editor.setCursor()
            
    class Next(ToolBase): 
        default_keymap = ''
        description = 'Next image...'
        def __init__(self, *args, gid, **kwargs): 
            super().__init__(*args, **kwargs)  
            self.ax = args[0].figure.axes[0] 
            
        def trigger(self, *args, **kwargs):   
            self.ax.editor.nextPage()  
            
    class OpenBox(ToolBase): 
        default_keymap = ''
        description = 'Open a file...'
        def __init__(self, *args, gid, **kwargs): 
            super().__init__(*args, **kwargs) 
            self.ax = args[0].figure.axes[0] 
        def trigger(self, *args, **kwargs): 
            self.ax.editor.openFile()
    
    class OtherBox(ToolBase):
        default_keymap = ''
        description = 'Identify other text areas'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "other"
            self.ax.editor.setCursor()
            
    class ParagraphBox(ToolBase): 
        default_keymap = ''
        description = 'Identify a paragraph'
        def __init__(self, *args, gid, **kwargs):

            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs)  
        def trigger(self, *args, **kwargs):       
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "paragraph"
            self.ax.editor.setCursor() 
            
    class Previous(ToolBase): 
        default_keymap = ''
        description = 'Previous image...'
        def __init__(self, *args, gid, **kwargs): 
            super().__init__(*args, **kwargs)  
            self.ax = args[0].figure.axes[0]
            
        def trigger(self, *args, **kwargs):  
            self.ax.editor.previousPage()  
            
    class SaveBox(ToolBase): 
        default_keymap = ''
        description = 'Save annotations...'
        def __init__(self, *args, gid, **kwargs): 
            super().__init__(*args, **kwargs)  
            self.ax = args[0].figure.axes[0]
            
        def trigger(self, *args, **kwargs):   
            self.ax.editor.save() 
      
    class SeparatorBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "separator"
            self.ax.editor.setCursor()
            
    class StaffNotationBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "staffNotation"
            self.ax.editor.setCursor()       
            
    class TablatureNotationBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "tablatureNotation"
            self.ax.editor.setCursor()
            
    class TableBox(ToolBase):
        default_keymap = ''
        description = 'Add a box to figure'
        def __init__(self, *args, gid, **kwargs):
            self.ax = args[0].figure.axes[0]
            self.ax.editor.boxTriggered = False
            super().__init__(*args, **kwargs) 

        def trigger(self, *args, **kwargs):          
            self.ax.editor.boxTriggered = True
            self.ax.editor.boxType = "table"
            self.ax.editor.setCursor() 
          
            
       

class PolygonInteractor(object):

    showverts = False
    epsilon = 5  # max pixel distance to count as a vertex hit

    def __init__(self, ax, poly, ocrRegion):
        if poly.figure is None:
            raise RuntimeError('You must first add a polygon to a figure '
                               'or canvas before defining the interactor')
        self.ax = ax
        canvas = poly.figure.canvas
        self.poly = poly
        self.ocrRegion = ocrRegion
        
        self.setPolygonCenter() 
        

        x, y = zip(*self.poly.xy)
        self.line = Line2D(x, y,
                           marker='o', color= 'black', markerfacecolor='r',
                           animated=False)
        self.ax.add_line(self.line)
        
        self.line.set_visible(self.showverts)

        self.cid = self.poly.add_callback(self.poly_changed)
        self._ind = None  # the active vert

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas
        
        self.canvas.draw_idle()

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        self._ind = self.get_ind_under_point(event)

    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if not self.showverts:
            return
        if event.button != 1:
            return
        self._ind = None
    
    def clearCoordinates(self): 
        self.line.set_visible(False)
        self.poly.remove()
        self.line.remove()
        self.poly.xy = np.array([[0,0],[0,0],[0,0],[0,0]]) # cannot make it unvisible otherwise ??? 
 
    def dist(self, x, y):
        """
        Return the distance between two points
        """
        d = x - y
        return np.sqrt(np.dot(d, d)) 
        #self.canvas.blit(self.ax.bbox)
    
    def dist_point_to_segment(self, p, s0, s1):
        """
        Get the distance of a point to a segment.
          *p*, *s0*, *s1* are *xy* sequences
        This algorithm from
        http://geomalgorithms.com/a02-_lines.html
        """
        v = s1 - s0
        w = p - s0
        c1 = np.dot(w, v)
        if c1 <= 0:
            return self.dist(p, s0)
        c2 = np.dot(v, v)
        if c2 <= c1:
            return self.dist(p, s1)
        b = c1 / c2
        pb = s0 + b * v
        return self.dist(p, pb)
    
    
    
    
    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
       
        # do not need to blit here, this will fire before the screen is
        # updated

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.hypot(xt - event.x, yt - event.y)
        indseq, = np.nonzero(d == d.min())
        ind = indseq[0]

        if d[ind] >= self.epsilon:
            ind = None

        return ind
    
    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes:
            return
        if event.key == 't':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts:
                self._ind = None
        elif event.key == 'd':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                
                self.poly.xy = np.delete(self.poly.xy,
                                         ind, axis=0)
                self.line.set_data(zip(*self.poly.xy))
                
        elif event.key == 'i':
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y  # display coords
            for i in range(len(xys) - 1):
                s0 = xys[i]
                s1 = xys[i + 1]
                d = self.dist_point_to_segment(p, s0, s1)
                if d <= self.epsilon:
                    self.poly.xy = np.insert(
                        self.poly.xy, i+1,
                        [event.xdata, event.ydata],
                        axis=0)
                    self.line.set_data(zip(*self.poly.xy))
                    break
        if self.line.stale:
            self.canvas.draw_idle()
            
    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts:
            return
        if self._ind is None:
            return
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        x, y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x, y
        if self._ind == 0:
            self.poly.xy[-1] = x, y
        elif self._ind == len(self.poly.xy) - 1:
            self.poly.xy[0] = x, y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.draw_idle() 
        self.ax.editor.unsaved()
        
    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)
        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state 
    

    def setPolygonCenter(self):  
        coordinates = self.poly.xy.tolist()
        xMax = coordinates[0][0]
        yMax = coordinates[0][1]
        xMin = coordinates[0][0]
        yMin = coordinates[0][1] 
        for coordinate in coordinates:
            if coordinate[0] > xMax: xMax = coordinate[0]
            if coordinate[0] < xMin: xMin = coordinate[0]
            if coordinate[1] > yMax: yMax = coordinate[1]
            if coordinate[1] < yMin: yMin = coordinate [1] 
        xDif = (xMax-xMin)/2    
        yDif = (yMax-yMin) / 2
        
        self.poly.centerCoordinates = [xMin+xDif, yMin+yDif]
        


class  SimpleChoiceBox():
    def SimpleChoiceBox(self, regionList, polygonInteractor):
         
        self.polygonType= None
        self.polygonOrder= None    
        self.regionList = regionList
        self.polygonInteractor = polygonInteractor
        self.ocrRegion = self.polygonInteractor.ocrRegion
        
         
        
        currentIndex = 0 
         
        self.master = tk.Tk()
        self.master.title("Region properties")
 
        tk.Label(self.master,text="Region name").grid(row=0)
        tk.Label(self.master,text="Reading order").grid(row=1)
         
        for counter, regionName in enumerate(self.regionList):
            if regionName == self.ocrRegion.regionName:
                currentIndex = counter
                break   
         
         
        self.comboBoxRegion = ttk.Combobox(self.master,  values=regionList, state='readonly')
        self.comboBoxRegion.current(currentIndex) 
        
        
        self.entry = tk.Entry(self.master)
        self.entry.insert(0, self.ocrRegion.index)

         
        self.comboBoxRegion.grid(row=0, column=1)
        self.entry.grid(row=1, column=1)
         
        tk.Button(self.master,  text='Cancel', command=self.master.quit).grid(row=3,  column=0, sticky=tk.W, pady=4)
        tk.Button(self.master, text='OK', command=self.show_entry_fields).grid(row=3,  column=1,  sticky=tk.W, pady=4)
        
        self.master.mainloop()
        self.master.destroy()
            
     
    def show_entry_fields(self):
        self.polygonType = self.comboBoxRegion.get()
        self.polygonOrder = int(self.entry.get())        
        self.master.quit()


class ReadWriteMets ():
    def __init__(self, xmlFilePath):
        self.xmlFilePath = xmlFilePath
        
        self.metsNameSpace = "http://www.loc.gov/METS/"
        self.metsNameEntry = "{http://www.loc.gov/METS/}"
        self.xlinkNameSpace = "http://www.w3.org/1999/xlink"
        self.xlinkNameEntry = "{http://www.w3.org/1999/xlink}"
        self.nameSpaceDictionary =  {"mets": self.metsNameSpace, "xlink": self.xlinkNameSpace}
        self.tree = ET.parse(xmlFilePath) 
    def getFileGroup (self, fileGroup="OCR-D-SEG-REGION"):
        self.fileGroupList = []   
        for groupeFile in self.tree.xpath('//mets:fileGrp[@USE="%s"]/mets:file/mets:FLocat' % (fileGroup), namespaces = self.nameSpaceDictionary): 
            if  "{http://www.w3.org/1999/xlink}href" in groupeFile.attrib: 
                self.fileGroupList.append(groupeFile.attrib["{http://www.w3.org/1999/xlink}href"])  
        return self.fileGroupList
        #


class ReadWritePageXML(object): 
    def __init__(self, xmlFilePath):
        self.pcNameSpace = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"
        self.pcNameEntry = "{http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15}"
        
        ''' read xml files '''
        self.xmlFilePath = xmlFilePath
        self.nameSpaceDictionary =  {"pc": self.pcNameSpace}
        self.regionRefDictionary = {}
        self.textRegionList = []
        self.regionDictionary = ["TextRegion", "GraphicRegion", "ImageRegion", "LineDrawingRegion", "MusicRegion", "TableRegion", "SeparatorRegion" ]
        
 
        self.tree = ET.parse(xmlFilePath)
        

    def getCoordinates(self):
        return self.coordinatesList
    
    def getImagePath(self): 
        ''' try to use de binarized image '''
        for alternativeImage in self.tree.xpath('//pc:Page/pc:AlternativeImage[@comments="binarized"]', namespaces = self.nameSpaceDictionary):
            if "filename" in alternativeImage.attrib: return alternativeImage.attrib["filename"]
            
        ''' if binarized image cannot be found, use original '''
        for ocrpage in self.tree.xpath('//pc:Page', namespaces = self.nameSpaceDictionary):
            if "imageFilename" in ocrpage.attrib: return ocrpage.attrib["imageFilename"]
            
        return None
        
    
    def readPageRegionXML(self): 
        ''' build reading order dictionary '''
        
        for regionRef in self.tree.xpath("//pc:RegionRefIndexed", namespaces = self.nameSpaceDictionary): 
            regionIndex = None
            regionReference = None
            
            if "index" in regionRef.attrib: regionIndex = regionRef.attrib["index"]
            if "regionRef" in regionRef.attrib: regionReference = regionRef.attrib["regionRef"]
            
            if regionIndex == None or regionReference == None: continue
            self.regionRefDictionary[regionReference] = regionIndex 
        
        
        ''' loop over every region of interest '''
        for region in self.regionDictionary:
        
            for regionClass in self.tree.xpath("//pc:" +region, namespaces = self.nameSpaceDictionary): 
                regionId = None
                regionType = None
                custom = None
                if "id" in regionClass.attrib: regionId = regionClass.attrib["id"]
                if "type" in regionClass.attrib: regionType = regionClass.attrib["type"]
                if "custom" in regionClass.attrib: custom = regionClass.attrib["custom"]
                 
                for coordinates in regionClass:
                    if coordinates.tag == self.pcNameEntry+"Coords":
                        if "points" in coordinates.attrib: 
                            coordsStringList = coordinates.attrib["points"].split(" ") 
                            coordinatesList = []
                            for coordinateString in coordsStringList: 
                                coordinatesList.append([int(i) for i in coordinateString.split(",")] )
                            regionIndex = None
                         
                            
                            if regionId in self.regionRefDictionary: 
                                regionIndex= self.regionRefDictionary[regionId]
                            else:
                                print ("region index not identified for region id" + regionId + " Skipping this region")
                                continue
                             
                            
                            self.textRegionList.append(TextRegion(coordinatesList, regionId, regionIndex, regionType, regionClass.tag.replace(self.pcNameEntry, ""), custom))
  
        return self.textRegionList
    
    
    def writePageRegionXML(self, polygoninteractorlist): 
        
        ''' clear RegionRefIndex and all Regions in element tree'''
        for regionRef in self.tree.xpath("//pc:RegionRefIndexed", namespaces = self.nameSpaceDictionary): 
            regionRef.getparent().remove(regionRef)
            
        for region in self.regionDictionary: 
            for regionClass in self.tree.xpath("//pc:" +region, namespaces = self.nameSpaceDictionary): 
                regionClass.getparent().remove(regionClass)
        
        ''' loop over every polygon interactor and add information to elementTree '''
                
        for polygonInteractor in polygoninteractorlist: 
            
            ''' add region index ''' 
            for orderedGroup in self.tree.xpath("//pc:OrderedGroup", namespaces = self.nameSpaceDictionary):
                orderedGroupElement = ET.Element(self.pcNameEntry+"RegionRefIndexed", attrib={"index":str(polygonInteractor.ocrRegion.index), "regionRef":polygonInteractor.ocrRegion.id} , nsmap = self.nameSpaceDictionary)
                orderedGroup.append(orderedGroupElement)
                
            ''' add page regions '''
            for pcPage in self.tree.xpath("//pc:Page", namespaces = self.nameSpaceDictionary):
                attributeDictionary = {"id":polygonInteractor.ocrRegion.id}#
                coordinatesString = ""
                for coordinates in polygonInteractor.ocrRegion.coordinates:
                    coordinatesString = coordinatesString + str(coordinates[0]) + "," + str(coordinates[1]) + " "
                
                coordinatesString = coordinatesString[:-1]
                
                
                if polygonInteractor.ocrRegion.type != None: attributeDictionary["type"]=polygonInteractor.ocrRegion.type
                if polygonInteractor.ocrRegion.custom != None: attributeDictionary["custom"]=polygonInteractor.ocrRegion.custom
                 
 
                pageRegion = ET.Element(self.pcNameEntry+polygonInteractor.ocrRegion.regionClass, attrib=attributeDictionary,nsmap = self.nameSpaceDictionary)
                coordinates=  ET.Element(self.pcNameEntry+"Coords",attrib={"points":coordinatesString},nsmap = self.nameSpaceDictionary)
                pageRegion.append(coordinates)
                pcPage.append(pageRegion)
                
                
        ''' write file '''
        self.tree.write(self.xmlFilePath) 
    
class TextRegion(object):
    def __init__(self, regionCoordinates,regionId, regionIndex, regionType, regionClass, custom=None):
        self.coordinates = regionCoordinates
        self.regionClass = regionClass
        self.type = regionType
        self.id = regionId
        self.index = int(regionIndex) 
        self.custom = custom
        self.regionName = None # this is not part of xml schema but used in matplot only 
        
        
        if self.regionClass == "TextRegion":
            if self.type in ["paragraph", "caption", "header", "heading", "footer", "drop-capital", "marginalia", "footnote", "other"]:
                self.regionName = self.type   
                
            else: self.regionName = "other"
        
        
        
        elif self.regionClass == "MusicRegion": 
            if self.custom=="staffNotation": self.regionName=  "staffNotation"
            elif self.custom == "tablatureNotation": self.regionName = "tablatureNotation"
                
        elif self.regionClass == "TableRegion": self.regionName = "table"
        elif self.regionClass == "GraphicRegion": self.regionName = "graphic"
        elif self.regionClass == "ImageRegion": self.regionName = "image"
        elif self.regionClass == "LineDrawingRegion": self.regionName = "linedrawing"
        elif self.regionClass == "SeparatorRegion": self.regionName = "separator"
        
       
        
        
        
 
