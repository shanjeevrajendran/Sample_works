#python
import sys
import os
import subprocess   
import traceback
import lx
from site import addsitedir
conda_path = os.path.expanduser('~\AppData')
sitedir = r""+conda_path+"\Local\Continuum\Anaconda2\Lib\site-packages"
try:
    addsitedir(sitedir)
    print "library added"
except:    
    sys.exit(0)
import xlrd  
      
def findId():
    sceneService = lx.Service("sceneservice")
    sceneService.select("scene", "main")
    arrayItems = lx.eval1( "query sceneservice item.N ?" )
    for item in xrange(arrayItems):
         sceneService.select("item", str(item))
         itemType = sceneService.query("item.type")
         itemID = sceneService.query("item.id")
         itemName = sceneService.query("item.name")
         print ("Found following layer: %s (Type: %s) (Id: %s)" % (itemName, itemType, itemID))

def importExcel(second_sheet, material):    
    try:
        for row_index in xrange(0, second_sheet.nrows):
        
            if second_sheet.cell(row_index,0).value == material:
                i = row_index
                Diffuse_amount    = second_sheet.cell(i,1).value
                Diffuse_color_R   = second_sheet.cell(i,2).value
                Diffuse_color_G   = second_sheet.cell(i,3).value
                Diffuse_color_B   = second_sheet.cell(i,4).value
                Specular_amount   = second_sheet.cell(i,5).value
                Specular_color_R  = second_sheet.cell(i,6).value
                Specular_color_G  = second_sheet.cell(i,7).value
                Specular_color_B  = second_sheet.cell(i,8).value
                Diffuse_roughness = second_sheet.cell(i,9).value
                Transparency      = second_sheet.cell(i,10).value
                Radiance          = second_sheet.cell(i,11).value
        print 'Exporting material properties'            
        return Diffuse_amount, Diffuse_color_R, Diffuse_color_G, Diffuse_color_B, Specular_amount, Specular_color_R, Specular_color_G, Specular_color_B, Diffuse_roughness, Transparency, Radiance
    except:
         dialogMaterial(material)
         
def cutomMaterialFunction(second_sheet, material):
    Diffuse_amount, Diffuse_color_R, Diffuse_color_G, Diffuse_color_B, Specular_amount, Specular_color_R, Specular_color_G, Specular_color_B, Diffuse_roughness, Transparency, Radiance = importExcel(second_sheet, material) 
    renderitem = lx.eval('query sceneservice render.id ? 0')
    lx.eval('shader.create advancedMaterial')
    lx.eval('item.name "'+material+'" advancedMaterial')
    lx.eval('texture.parent %s -1' %renderitem)
    lx.eval('item.channel advancedMaterial$diffAmt %s'%Diffuse_amount) # Diffuse Amount
    lx.eval('item.channel advancedMaterial$diffCol {%s %s %s}'%(Diffuse_color_R,Diffuse_color_G,Diffuse_color_B)) # Diffuse Color
    lx.eval('item.channel advancedMaterial$specAmt %s'%Specular_amount) # Specular Amount
    lx.eval('item.channel advancedMaterial$specCol {%s %s %s}'%(Specular_color_R,Specular_color_G,Specular_color_B)) # Specular Color
    lx.eval('item.channel advancedMaterial$rough %s'%Diffuse_roughness) # Diffuse Roughness
    lx.eval('item.channel advancedMaterial$tranAmt %s'%Transparency) # Transparency
    lx.eval('item.channel advancedMaterial$specFres 1.0')
    lx.eval('item.channel advancedMaterial$radiance %s'%Radiance)#radiance
    lx.eval('item.channel advancedMaterial$bumpAmp 0.005')#
    lx.eval('view3d.shadingStyle advgl') # Important to make wires visible through surfaces
    lx.eval('view3d.wireframeAlpha 1 active') # Important to make wires visible through surfaces
    lx.eval('select.drop item advancedMaterial')
    lx.eval('select.drop item polyRender')
    
def setNoise(material):
    lx.eval('select.item {'+material+'} set  :advancedMaterial') 
    lx.eval('shader.create noise')
    lx.eval('shader.setEffect bump')
    lx.eval('item.channel noise$value1 -0.1')
    lx.eval('item.channel noise$value2 0.1')
    lx.eval('item.channel noise$type simple')

    lx.eval('select.drop item')
    lx.eval('select.drop channel')
    lx.eval('select.drop envkey')

def dialogMaterial(material): 
    lx.eval('dialog.setup info')
    lx.eval('dialog.title {Confirm Material}')
    lx.eval('dialog.msg {Please mention the correct material or define the properties in the Requirements excel for "'+material+'"}')

    lx.eval('dialog.open')
    lx.eval("dialog.result ?")

def presetPath(material):
    m_path = ""                                                                                                
    r = [] 
#    folder = os.path.expanduser('~\\Documents\\') 
#    dir = folder+"Luxology\Content\Assets\Materials"     
    folder = os.path.expanduser('~\\Desktop\\') 
    dir = folder+"CAD TO MODO TEST COLLECT\CAD TO MODO TEST COLLECT\PRESETS"                                                                                                          
    subdirs = [x[0] for x in os.walk(dir)]  
    component = material.title()                                                                          
    for subdir in subdirs:                                                                                            
        files = os.walk(subdir).next()[2]                                                                             
        if (len(files) > 0):                                                                                          
            for file in files:
                if file.endswith(".lxp") and component in file: 
                    r.append(subdir + "\\" + file)
                    print r.count
                    if file.endswith(".lxp") and len(component.split()) >= 2:
                        m_path = subdir + "\\" + file
                    else:
                        m_path = subdir + "\\" + component + ".lxp"                                                                   
    return m_path  
    
def selectId(item_type, item_Name):
    global Id
    sceneService = lx.Service("sceneservice")
    sceneService.select("scene", "main")
    arrayItems = lx.eval1( "query sceneservice item.N ?" )
    for item in xrange(arrayItems):
         sceneService.select("item", str(item))
         itemType = sceneService.query("item.type")
         itemID = sceneService.query("item.id")
         itemName = sceneService.query("item.name")
         if item_type =="advancedMaterial" and itemName == "Base Material":
             lx.out("Found following Material: %s and Id %s" % (itemName,itemID) )
             lx.command( "select.item", item=itemID )
             Id = itemID
         else:
             if itemType == item_type and itemName == item_Name:
                 lx.out("Found following Material: %s and Id %s" % (itemName,itemID) )
                 lx.command( "select.item", item=itemID )
                 Id = itemID
    print ("******Found Id******* : ",Id)
    return Id          
    pass        
   
def applyPreset(m_path,Id, file_base_name):
    print('Accesing preset browser')
    lx.eval('preset.dropShader servername:"$LXP" filename:"'+m_path+'" hititem:{'+file_base_name+':root} material:'+Id+' mode:{apply}')
    print ("m_path :"+m_path+"")
   
def saveLxo(file_base_name):
    loc = 'D:\MODO\Output'
    loc = convertPath(loc)
    path = loc+file_base_name
    o_path =path + ".lxo"
    try:
        os.remove(o_path)
    except OSError:
        pass
    lx.eval("scene.saveAs {"+o_path+"} $LXOB false")
    print '***************************Closing scene***************************'
  
def render(file_base_name):
    loc = 'D:\MODO\Output'
    loc = convertPath(loc)
    path = loc+file_base_name
#    lx.eval('shader.create renderOutput')
#    lx.eval('shader.create defaultShader')
#    itemId = selectId(item_type = "renderOutput",item_Name =  "Final Color Output")
#    restoreGamma(itemId)
    lx.command("render", filename=loc + file_base_name, format="TIF")
    print 'Saving rendered output'
    return path    
    
def rename(path):
    file_name = path +".tif"
    try:
        os.remove(file_name)
    except OSError:
        pass
    os.rename(path +"Final Color Output0000.tif", file_name)
    print 'Renaming TIFF files to file name'

def restoreGamma(render_Id):
    lx.eval('select.subItem '+render_Id+' set textureLayer;render;environment;light;camera;scene;replicator;mediaClip;txtrLocator')
    lx.eval('item.channel renderOutput$gamma 2.2')
    print 'Applying Gamma correction'
    
def renderCamera(itemID):
    lx.command( "select.item", item=itemID )
#    lx.command ("render.camera", camera=itemID)
    lx.eval('tool.set TransformItem on')
    lx.eval('tool.set TransformMoveItem on')
#    lx.eval('item.channel camera$focalLen 0.04')
    lx.eval('item.channel camera$filmFit overscan')
#    lx.eval('item.channel camera$dof true')
#    lx.eval('camera.autofocus')
    print 'Adjusting render camera to fit frame'

def close():
    lx.eval( "app.quit" )
    
def log():
    lx.eval1( "log.toConsole true" )
    print '************************Execution started***************************'

def openFile(file_base_name):
    model_loc  = 'D:\MODO\Model'
    scene_path =  r"C:\Users\672458\Desktop\CAD TO MODO TEST COLLECT\CAD TO MODO TEST COLLECT\CAD_MasterStage.lxo"   
    extension = ".sldprt"
    path = convertPath(model_loc)
    path = path + file_base_name + extension
    lx.eval('scene.open {'+scene_path+'} normal')
    lx.eval('scene.importReference {'+path+'} true false false false false')
    print '******************Opening '+file_base_name+'.sldprt*****************'
    return path
    
def convertPath(path):
    path = path.split('\\')
    path = '\\'.join(path)
    path = path +"\\"
    print 'Normalizing the folder path'
    print "convertpath:"+path
    return path
    
def openOutput():
    loc = 'D:\MODO\Output'
    loc = convertPath(loc)
    print 'Opening output'
    subprocess.Popen(r'explorer \select,'+loc+'')
    
def scaleRatio(sub_item): 
    lx.eval('select.subItem '+sub_item+' set mesh;triSurf;meshInst;camera;light;txtrLocator;backdrop;groupLocator;replicator;surfGen;locator;deform;locdeform;deformGroup;deformMDD2;morphDeform;itemInfluence;genInfluence;deform.wrap;softLag;modSculpt;ABCCurvesDeform.sample;ABCdeform.sample;force.root;baseVolume;chanModify;itemModify;chanEffect;defaultShader;defaultShader 0 0')
    lx.eval('xref.manageOptions always always always always always')
    lx.eval('item.setType mesh locator')
    lx.eval('center.bbox center')
    lx.eval('transform.channel pos.Y 0.0')
    lx.eval('transform.channel pos.X 0.0')
    lx.eval('transform.channel pos.Z 0.0')
    ratio = str(dimensions())
    lx.eval('transform.channel name:{rot.X} value:-90.0')
    lx.eval('transform.channel name:{scl.X} value:'+ratio+' mode:scale ')
    lx.eval('transform.channel name:{scl.Y} value:'+ratio+' mode:scale ')
    lx.eval('transform.channel name:{scl.Z} value:'+ratio+' mode:scale ')

def dimensions():
    target_x = 0.89034
    target_y = 0.81223
    target_z = 0.51408
    lx.eval("@absolute.pl grab")
    valx = lx.eval("user.value lux_absolute_size_X ?")
    valy = lx.eval("user.value lux_absolute_size_Y ?")
    valz = lx.eval("user.value lux_absolute_size_Z ?")
    x = float(valx)
    y = float(valy)
    z = float(valz)
    print x, y ,z
   
    a = y
    y = z
    z = a  
    x_ratio  = target_x/x
    y_ratio  = target_y/y
    z_ratio  = target_z/z
    max_no   = min(x_ratio,y_ratio,z_ratio) 
    ratio    = max_no     
    return ratio
    
def applyProp(file_base_name,second_sheet, material):
    global m_path
    global Camera_Id
    global path 
    Id = ""
    openFile(file_base_name)
    m_path = presetPath(material)
    if m_path == "":
        cutomMaterialFunction(second_sheet, material)
        setNoise(material)
    else:
        m_path = presetPath(material)
        Id = selectId(item_type = "advancedMaterial",item_Name = "Base Material")
        print('Accesing preset browser')
        applyPreset(m_path,Id, file_base_name)
    sub_item = '{'+file_base_name+':root}'
    scaleRatio(sub_item)
    saveLxo(file_base_name)
    lx.eval1("scene.close")

def log_save():
    lx.eval('log.masterSave "D:\MODO\Output\log.txt"')
    lx.eval1("log.toConsole false" )
    
def main():
    log()
    loc = "D:\MODO\Req_excel"
    loc = convertPath(loc)
    ecfile = loc + "Requirements.xlsx"
    book = xlrd.open_workbook(ecfile)
    first_sheet = book.sheet_by_index(0)
    second_sheet= book.sheet_by_index(1)
    for row_i in xrange(1, first_sheet.nrows):
        i = row_i
        file_base_name = first_sheet.cell(i,0).value 
        material = first_sheet.cell(i,1).value 
        applyProp(file_base_name,second_sheet, material) 
    openOutput()
    log_save()
    close()

    pass

if __name__ == '__main__':
   try:
      main()
   except:
      print sys.exc_info()[0]
      print traceback.format_exc()