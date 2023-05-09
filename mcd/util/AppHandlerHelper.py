import bpy

def RefreshHandlerCallbacks(handlerss, callbacks):
    for handlers in handlerss:
        for callback in callbacks:
            [handlers.remove(h) for h in handlers if h.__name__ == callback.__name__] # TODO: purge the and name from func below
            handlers.append(callback)

def RefreshLoadPostHandler(callback):
    RefreshHandlerCallbacks([bpy.app.handlers.load_post], [callback])

# Debug
def ClearAllLoadPostHandlers():
    handlers = bpy.app.handlers.load_post
    [handlers.remove(h) for h in handlers]


# REMINDER: how to depsgraph
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