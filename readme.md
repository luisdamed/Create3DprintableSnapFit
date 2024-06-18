# Shortcut to create snap-fit tabs in Autodesk Fusion for 3D printing

## Work in progress

To-do:

- Implement selection of skecth point for tab-centering (Done 20240618)
  - To improve selection of inner sketch profiles. At the moment changing the behavior of auto-project geometry changes index of sketch profiles for selection:
    - If autoproject is disabled, selection starts from `sketchObj.profiles.item(0)`
    - If autoproject is enabled, selection must start from `sketchObj.profiles.item(1)` to skip the outer contour of the face
    - If the sketch is not on a face, then autoproject setting has no effect.
- Create fillets on extruded tabs
- Check parametrical linking on Fusion GUI
- Ask user to select base body for male and female tabs
- Perform Boolean operations using the created tabs
- Add images to illustrate where the dimensions are located
- Show images in input dialogue windows for reference
