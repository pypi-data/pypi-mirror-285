import gamma

#
# create a player entity to control the menu
#

playerEntity = gamma.Entity()
playerEntity.addComponent(gamma.InputComponent(up=gamma.keys.up, down=gamma.keys.down, left=gamma.keys.left, right=gamma.keys.right, b1=gamma.keys.enter))

#
# create some functions to attach to the menu buttons
#

def changeTextColour():
    if mainScene.textColour == gamma.WHITE:
        mainScene.textColour = gamma.LIGHT_GREY
    else:
        mainScene.textColour = gamma.WHITE

def changeBackgroundColour(colour):
    mainScene.background = colour

#
# create a main scene
#

class MainScene(gamma.Scene):

    def init(self):
        self.textColour = gamma.WHITE
        self.background = gamma.BLUE
        self.setMenu(gamma.Menu(300,150,
            [
                gamma.UITextMenuItem('Change title text colour', actionListener=gamma.ActionListener(changeTextColour)),
                gamma.UITextMenuItem('Change background to Dark Grey', actionListener=gamma.ActionListener(lambda: changeBackgroundColour(gamma.DARK_GREY))),
                gamma.UITextMenuItem('Change background to Blue', actionListener=gamma.ActionListener(lambda: changeBackgroundColour(gamma.BLUE)))
            ]
        , entities=[playerEntity]), self)

    def draw(self):
        self.renderer.add(gamma.Text('Choose an option:', 25, 25, colour=self.textColour))

#
# add scene to the engine and start
#

mainScene = MainScene()
gamma.init((600, 400), caption='Gamma // Menu Example')
gamma.sceneManager.push(mainScene)
gamma.run()