
from conf import settings


def arrow(x1, y1, x2, y2, arrow_offset=0, label="", selected=False, label_offset=0):
    if selected:
        strokeWeight(6)
        stroke(settings.SELECTED_COLOR)
        fill(0)
        line(x1, y1, x2, y2)
        pushMatrix()
        translate(x2, y2)
        rotate(atan2(y2-y1, x2-x1))
        translate(-arrow_offset, 0)
        stroke(settings.SELECTED_COLOR)
        fill(settings.SELECTED_COLOR)
        triangle(4, 0, -12, 7, -12, -7)
        popMatrix()
    strokeWeight(2)
    stroke(0)
    fill(0)
    line(x1, y1, x2, y2)
    pushMatrix()
    translate(x2, y2)
    rotate(atan2(y2-y1, x2-x1))
    pushMatrix()
    translate(-arrow_offset, 0)
    stroke(0)
    fill(0)
    triangle(0, 0, -10, 5, -10, -5)
    popMatrix()
    translate(-sqrt((y2-y1)**2 + (x2-x1)**2)/2.0, 0)
    text(label, -textWidth(label) / 2, -(settings.TEXT_SIZE * 0.5) - settings.TEXT_SIZE * label_offset)
    popMatrix()


class Wheel(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_menu_selection(self):
        if mouseX < self.x and mouseY < self.y:
            return "New"
        elif mouseX > self.x and mouseY > self.y:
            return "Save"
        elif mouseX > self.x and mouseY < self.y:
            return "Load"
        return None

    def draw(self, controller):
        if self.x and self.y:
            noFill()
            stroke(0)
            strokeWeight(2)
            ellipse(self.x, self.y, 100, 100)
            textSize(settings.TEXT_SIZE)
            text("New", self.x - 55, self.y - 55)
            text("Save", self.x + 55, self.y + 55 + settings.TEXT_SIZE)
            text("Load", self.x + 55, self.y - 55)
            line(self.x, self.y, self.x + 50, self.y)
            line(self.x, self.y, self.x - 50, self.y)
            line(self.x, self.y, self.x, self.y - 50)
            line(self.x, self.y, self.x, self.y + 50)
            line(self.x, self.y, mouseX, mouseY)
