#Author- Luis Medina
#Description- Shortcut for creating a simple snap fit for 3D printing

import adsk.core, adsk.fusion, adsk.cam, traceback


def createUserParams(designObj,tabWidth, tabHeight, tabClearance):
    # Create Value Input objects from user input
    tabWidth_val = adsk.core.ValueInput.createByString(tabWidth[0])
    tabHeight_val = adsk.core.ValueInput.createByString(tabHeight[0])
    tabClearance_val = adsk.core.ValueInput.createByString(tabClearance[0])
    
    # Create user parameters to make the tab parametric
    tabWidth_param = designObj.userParameters.add("tabWidth", 
                                        tabWidth_val,
                                        "mm",
                                        "Width of snap-fit tab")
    
    tabHeight_param = designObj.userParameters.add("tabHeight", 
                                        tabHeight_val,
                                        "mm",
                                        "Height of snap-fit tab")
    
    
    tabClearance_param = designObj.userParameters.add("tabClearance", 
                                        tabClearance_val,
                                        "mm",
                                        "Height of snap-fit tab")

    
    return {"width":tabWidth_param, 
            "height": tabHeight_param, 
            "clearance": tabClearance_param}



def createTabSketch(sketch, point, widthParam, 
                    heightParan, clearanceParam):
        
    # Define start and end points for male tab
    try:
        tabStartPoint = point

    except:
        tabStartPoint = adsk.core.Point3D.create(0,0,0)
    
    # tabStartPoint = adsk.core.Point3D.create(point.entity.geometry.x,
    #                                          point.entity.geometry.y,
    #                                          point.entity.geometry.z)
    maleTabEndPoint = adsk.core.Point3D.create(tabStartPoint.asArray()[0] + widthParam.value/2,
                                            tabStartPoint.asArray()[1] + heightParan.value/2,
                                            0)
    
    # Define start and end points for female tab
    femaleTabEndPoint = adsk.core.Point3D.create(
                tabStartPoint.asArray()[0] + widthParam.value/2 + clearanceParam.value,
                tabStartPoint.asArray()[1] + heightParan.value/2 + clearanceParam.value,
                                                          0)
    sketchLines = sketch.sketchCurves.sketchLines

    # Create Center-point rectangle the size of the tab
    maleTabSketch = sketchLines.addCenterPointRectangle(
                                                tabStartPoint, 
                                                maleTabEndPoint)
    
    sketch.geometricConstraints.addHorizontal(maleTabSketch.item(0))
    sketch.geometricConstraints.addHorizontal(maleTabSketch.item(2))
    sketch.geometricConstraints.addVertical(maleTabSketch.item(1))
    sketch.geometricConstraints.addVertical(maleTabSketch.item(3))
    
    # Create offset rectangle for female tab
    femaleTabSketch = sketchLines.addCenterPointRectangle(
                                                tabStartPoint,
                                                femaleTabEndPoint)
    
    sketch.geometricConstraints.addHorizontal(femaleTabSketch.item(0))
    sketch.geometricConstraints.addHorizontal(femaleTabSketch.item(2))
    sketch.geometricConstraints.addVertical(femaleTabSketch.item(1))
    sketch.geometricConstraints.addVertical(femaleTabSketch.item(3))
    
    sketch.sketchDimensions.addDistanceDimension(femaleTabSketch.item(0).startSketchPoint, femaleTabSketch.item(0).endSketchPoint,
                                                     adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation,
                                                     adsk.core.Point3D.create(widthParam.value, 0, 0))

    return (maleTabSketch, femaleTabSketch)


def extrudeTabs(sketchObj, extrusionsObj, heightParam, 
                clearanceParam, maleColor, femaleColor):
        # Create Inputs for extrusion
        heightInput = adsk.core.ValueInput.createByString(heightParam.name + 
                                                          "+" +
                                                          clearanceParam.name)
        deg0 = adsk.core.ValueInput.createByString("-45 deg")
        extent_distance = adsk.fusion.DistanceExtentDefinition.create(heightInput)



        # Get the profile defined by the outer tab
        maleProfile = sketchObj.profiles.item(1)

        # Create an object collection to use an input for the inner tab
        femaleProfile = adsk.core.ObjectCollection.create()
        
        # Add all of the profiles to the collection.
        for i_prof, prof in enumerate(sketchObj.profiles):
            if i_prof > 0:
                femaleProfile.add(prof)
      


        
        maleExtrudeInput = extrusionsObj.createInput(maleProfile, 
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        femaleExtrudeInput = extrusionsObj.createInput(femaleProfile, 
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        maleExtrudeInput.setOneSideExtent(extent_distance, 
                adsk.fusion.ExtentDirections.PositiveExtentDirection,
                                      deg0)
        
        femaleExtrudeInput.setOneSideExtent(extent_distance, 
                adsk.fusion.ExtentDirections.PositiveExtentDirection,
                                      deg0)
        
        maleExtrude = extrusionsObj.add(maleExtrudeInput)
        femaleExtrude = extrusionsObj.add(femaleExtrudeInput)

        # Get the extrusion body
        maleTabBody = maleExtrude.bodies.item(0)
        maleTabBody.name = "MaleTab_Combine"
        
        maleTabBody.appearance = maleColor
        femaleTabBody = femaleExtrude.bodies.item(0)
        femaleTabBody.name = "FemaleTab_Cut"
        femaleTabBody.appearance = femaleColor

        return (maleTabBody, femaleTabBody)

def run(context):
    ui = None
    try:
        # Access running instance of Fusion
        app = adsk.core.Application.get()

        # Access user interface
        ui  = app.userInterface

        # Access current document
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        # Access root component in the current design
        rootComp = design.rootComponent

        # Get extrusion features
        extrusions = rootComp.features.extrudeFeatures

        # Get appearances
        fusionMaterials = app.materialLibraries.itemByName('Fusion Appearance Library')
        redColor = fusionMaterials.appearances.itemByName('Paint - Enamel Glossy (Red)')
        blueColor = fusionMaterials.appearances.itemByName('Paint - Enamel Glossy (Blue)')  

        # Check if a Sketch is currently selected
        if app.activeEditObject.objectType != adsk.fusion.Sketch.classType():
            ui.messageBox('A sketch must be active. Edit a sketch and retry') 
            return
        
        # Get current sketch and sketch components
        sketch = adsk.fusion.Sketch.cast(app.activeEditObject)

        # # Ask the user to input the dimensions for the snap hook tab
        tabWidth = ui.inputBox('Input tab width in mm: ', 
                                    'Tab width', '5')
        tabHeight = ui.inputBox('Input tab height in mm: ', 
                                    'Tab height', '2')
        tabClearance = ui.inputBox('Input tab clearance in mm: ', 
                                    'Tab clearance', '0.2')
        
        Selection = ui.selectEntity('Select Point for centering', 'SketchPoints')
        

        ClickPoint = adsk.core.Point3D.create(Selection.entity.geometry.x,
                                             Selection.entity.geometry.y,
                                             Selection.entity.geometry.z)
        
        # Create new user parameters
        newParams = createUserParams(design, tabWidth, 
                                     tabHeight, tabClearance)
        
        # Create base sketches to extrude from
        tabSketch = createTabSketch(sketch ,ClickPoint, newParams["width"], 
                                     newParams["height"], newParams["clearance"])

        # Extrude tab bodies
        extrudeTabs(sketch, extrusions, newParams["height"], 
                newParams["clearance"], blueColor, redColor)
        

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
