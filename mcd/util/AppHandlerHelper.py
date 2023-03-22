import bpy

def RefreshHandlerCallbacks(handlerss, callbackAndNames):
    # h = bpy.app.handlers
    # handlers = [
    #     h.depsgraph_update_pre,         # handler for any click on the uilist
    #     # h.load_post  # sadly this doesn't do anything because there's no 'scene' object when load_post fires
    #     ]
    # for handlers in handlers:
    #     [handlers.remove(h) for h in handlers if h.__name__ == "syncDisplayKVs"]
    #     handlers.append(syncDisplayKVs)

    # for handlers in handlers:
    #     [handlers.remove(h) for h in handlers if h.__name__ == "handleSelectionChanged"]
    #     handlers.append(handleSelectionChanged)
    for handlers in handlerss:
        for callbackAndName in callbackAndNames:
            [handlers.remove(h) for h in handlers if h.__name__ == callbackAndName[1]]
            handlers.append(callbackAndName[0])

def RefreshLoadPostHandlers(callbackAndName):
    RefreshHandlerCallbacks([bpy.app.handlers.load_post], [callbackAndName])
