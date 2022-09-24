from messages import SayText2


def load():
    SayText2('Plugin has been loaded successfully!').send()


def unload():
    SayText2('Plugin has been unloaded successfully!').send()
