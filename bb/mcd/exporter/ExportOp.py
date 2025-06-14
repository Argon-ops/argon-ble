from bb.mcd.core.command.CUSTOM_PG_AS_Collection import PlayablesExporter
from bb.mcd.settings.GlobalSettings import GlobalSettingsExporter
from bb.mcd.core.materiallist.MaterialList import MaterialListExporter
from bb.mcd.core.componentlike.preexport.ComponentLikePreExport import ComponentLikePreExport
from bb.mcd.settings.IsArgonMarker import IsArgonMarker


def PreExport(targetDataHolder):
    """Prepare for export

        Some data (e.g. playables) are stored in
          lists that don't read directly from a custom property. 
          So, write these lists to a custom property before exporting.
        (Unfortunately, this means the client has to use our export button;
            can't use the vanilla fbx exporter directly.)
    """

    IsArgonMarker.PreExport(targetDataHolder)

    GlobalSettingsExporter.PreExport(targetDataHolder)

    PlayablesExporter.PreExport(targetDataHolder)

    MaterialListExporter.PreExport(targetDataHolder)

    ComponentLikePreExport.PreExport(targetDataHolder)


def PostExport(targetDataHolder):
    pass
    # actually we can't do much post-export because we don't know
    #   how to get a call back after a modal, file browser dialog...
    #   We don't have this problem with the Edy J exporter, because we
    #     have modified the actual exporter in our copy of his module
    #  We could make our own launcher for the vanilla fbx exporter...so that we would
    #   run the dialog part of the default fbx launcher...and just call the op without 'INVOKE_DEFAULT'
    # ASC.PlayablesExporter.CleanUpTargetObject(targetDataHolder)
