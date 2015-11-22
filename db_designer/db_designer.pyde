

import logging
from db_designer_fsm import Start
from models import Application

page_height = 768
page_width = 1024

application = None


def setup():
    global application
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Debug logging enabled")
    frame.setResizable(True)
    frameRate(30)
    size(page_width, page_height, FX2D)

    application = Application()
    application.changeState(Start)
    frame.setTitle(application.app_name)
    logging.debug("setup completed")


def scale_and_pan():
    scale(application.scaleXY)
    translate(application.panX, application.panY)


def draw():
    application.mousePX = mouseX / application.scaleXY - application.panX
    application.mousePY = mouseY / application.scaleXY - application.panY
    frame.setTitle(application.app_name)
    background(126)
    pushMatrix()
    scale_and_pan()
    for table in application.tables:
        for column in table.columns:
            for connector in column.connectors:
                connector.draw(application)
    for table in application.tables:
        table.draw(application)
    popMatrix()
    application.draw(application)
    scale_and_pan()


def mousePressed():
    application.state.mousePressed(application)


def mouseDragged():
    application.state.mouseDragged(application)


def mouseReleased():
    application.state.mouseReleased(application)


def keyPressed():
    application.state.keyPressed(application)


def keyReleased():
    application.state.keyReleased(application)


def keyTyped():
    application.state.keyTyped(application)


def fileSelected(selection):
    application.state.fileSelected(application, selection)
