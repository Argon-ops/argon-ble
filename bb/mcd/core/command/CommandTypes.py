

def getPlayableTypes():
    return (
        ('0', 'Event Only', 'Nothing to play. Just generate an event'),
        ('1', 'Animation', 'Animation and/or audio'),
        ('2', 'Looping Animation', 'Looping animation and/or audio'),
        ('3', 'Send Signal', 'Send a signal to target objects'),
        ('4', 'Camera Shake', 'Trigger a camera shake'),
        ('5', 'Screen Overlay', 'Screen overlay'),
        ('6', 'Send Sleep/Wake-up Signal', 'Send a sleep or wake-up signal to targets'),
        ('7', 'Display Headline', 'Display text in the center of the screen'),
        ('8', 'Message Bus', 'Send a message on the MessageBus'),
        ('9', 'Send Destroy Signal', 'Send a destroy signal to the targets'),
        ('10', 'Command Group', 'A command that invokes a set of commands'),
        ('11', 'Wait Seconds', 'Waits for the given number of seconds'),
        ('12', 'Cut Scene', 'Plays a cutscene'),
        ('13', 'Pose Animation TODO: impl', 'Pose an animation at a specific frame'),
    )