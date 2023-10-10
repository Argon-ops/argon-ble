from mcd.ui.actionstarterlist.CUSTOM_PG_AS_Collection import PlayablesExporter 
from mcd.settings.GlobalSettings import GlobalSettingsExporter 
from mcd.ui.materiallist.MaterialList import MaterialListExporter

#TODO: we're getting too many animations exported
#  for each action the action applies to more animations than we intended
#  Propose a bandaid for this: send Unity a look up with each objects animation data
#   (since it seems like the animations listed per object are the 'real' ones that we intended)

def PreExport(targetDataHolder):
  """Make sure that everything is ready to be exported
      
      Some data (playables) exists
        as a list that doesn't read directly from a custom property. 
        Make sure that the custom property for each playable reflects 
        the state of the playables list.
      UNFORTUNATELY: this means the client has to use our export button;
          can't use the vanilla fbx exporter directly.
  """

  GlobalSettingsExporter.PreExport(targetDataHolder)

  PlayablesExporter.PreExport(targetDataHolder)

  MaterialListExporter.PreExport(targetDataHolder)


  print(F"########################################")
  print(F"#####Pre export ########################")
  print(F"########################################")
  # CUSTOM_PG_AS_Collection.syncPlayables()

  # from mcd.objectinfo import ObjectInfo
  # ObjectInfo.writeObjectInfo(context)

def PostExport(targetDataHolder):
  pass
  # sadly we can't do much post export because we don't know 
  #   how to get a call back after a modal, file browser dialog...
  #   We don't have this problem with the Edy J exporter, because we 
  #     have modified the actual exporter in our copy of his module
  #  We could make our own launcher for the fbx exporter...so that we would 
  #   run the dialog part of the default fbx launcher...and just call the op without 'INVOKE_DEFAULT'
  # ASC.PlayablesExporter.CleanUpTargetObject(targetDataHolder)
