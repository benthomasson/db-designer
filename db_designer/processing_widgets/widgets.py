

from math import pi

import button_fsm


class Widget(object):

    def mouseOver(self):
        pass

    def mouseOut(self):
        pass

    def mousePressed(self):
        pass

    def mouseReleased(self):
        pass

    @property
    def top_extent(self):
        pass

    @property
    def bottom_extent(self):
        pass

    @property
    def left_extent(self):
        pass

    @property
    def right_extent(self):
        pass


class Button(Widget, button_fsm.Controller):

    def __init__(self, x, y, label, text_size=20, size=20, color="#5A5A5A", fill="#B9B9B9", pressed_color="#7F7F7F", call_back=None):
        self.x = x
        self.y = y
        self.text_size = text_size
        self.label = label
        self.color = color
        self.fill = fill
        self.size = size
        self.pressed_color = pressed_color
        self.state = button_fsm.NotPressed
        self.pressed = False
        self.active = False
        self.call_back = call_back

    def mouseOver(self):
        self.active = True

    def mouseOut(self):
        self.active = False
        self.state.mouseOut(self)

    def mousePressed(self):
        self.state.mousePressed(self)

    def mouseReleased(self):
        self.state.mouseReleased(self)

    @property
    def top_extent(self):
        return self.y

    @property
    def left_extent(self):
        return self.x

    @property
    def right_extent(self):
        textSize(self.text_size)
        return self.x + textWidth(self.label) + self.size

    @property
    def bottom_extent(self):
        return self.y + self.size + self.text_size

    @property
    def width(self):
        return self.right_extent - self.left_extent

    @property
    def height(self):
        return self.bottom_extent - self.top_extent

    def draw(self):
        self.draw_button()
        self.draw_icon()
        self.draw_label()

    def draw_button(self):
        pushMatrix()
        translate(self.x, self.y)
        if self.active:
            stroke(self.color)
        else:
            stroke(self.fill)
        if self.pressed:
            fill(self.pressed_color)
        else:
            fill(self.fill)
        textSize(self.text_size)
        rect(0, 0, self.width, self.height, self.size/5)
        popMatrix()

    def draw_icon(self):
        pass

    def draw_label(self):
        pushMatrix()
        translate(self.x, self.y)
        translate((textWidth(self.label) + self.size) / 2,
                  (self.size + self.text_size) / 2 - self.text_size / 4)
        textAlign(CENTER, CENTER)
        fill(self.color)
        text(self.label, 0, 0)
        popMatrix()
        textAlign(LEFT, BASELINE)


def button(x, y, label, text_size=20, size=20, color="#5A5A5A", fill="#B9B9B9"):
    Button(x, y, label, text_size, size, color, fill).draw()


class NotificationCount(object):

    def __init__(self, x, y, count=0, size=20):
        self.x = x
        self.y = y
        self.count = count
        self.size = size

    def draw(self):
        pushMatrix()
        translate(self.x, self.y)
        textAlign(CENTER, CENTER)
        stroke("#FF5000")
        fill("#FF5000")
        count_str = str(self.count)
        textSize(int(self.size * 3 / 4))
        ellipse(-textWidth(count_str) / 2, 0, self.size, self.size)
        rect(-textWidth(count_str) / 2, -self.size /
             2, textWidth(count_str), self.size)
        ellipse(textWidth(count_str) / 2, 0, self.size, self.size)
        translate(0, -self.size / 10)
        fill(255)
        text(count_str, 0, 0)
        popMatrix()
        textAlign(LEFT, BASELINE)


def notification_count(x, y, count):
    NotificationCount(x, y, count).draw()


class ButtonBar(object):

    def __init__(self, buttons, x=0, y=0, size=50, color="#5A5A5A", fill="#B9B9B9", padding=5):
        self.x = x
        self.y = y
        self.color = color
        self.fill = fill
        self.size = size
        self.padding = padding
        self.buttons = []
        self.buttons.extend(buttons)

    def draw(self):
        strokeWeight(2)
        fill(self.fill)
        noStroke()
        rect(self.x, self.y, sum([b.width + self.padding for b in self.buttons]) + self.padding, self.size, self.size/5)
        x = self.x + self.padding
        y = self.y + self.padding
        for button in self.buttons:
            button.x = x
            button.y = y
            button.draw()
            x += button.width + self.padding


class SelectionButton(Button):

    def __init__(self, x, y, size=20, color="#5A5A5A", **kwargs):
        Button.__init__(self, x, y, "", size=size, color=color, **kwargs)

    @property
    def right_extent(self):
        return self.x + self.size + self.text_size

    def draw_icon(self):
        pushMatrix()
        x = self.x
        y = self.y
        strokeWeight(2)
        stroke(self.color)
        fill(self.color)
        translate(x, y)
        translate(self.width/2, self.height/2)
        rotate(pi/3)
        rotate(pi)
        translate(-self.size/2, 0)
        line(self.size, 0, 0, 0)
        pushMatrix()
        translate(self.size, 0)
        triangle(0, 0, -10, 5, -10, -5)
        popMatrix()
        popMatrix()


class MoveButton(Button):

    def __init__(self, x, y, size=20, color="#5A5A5A", **kwargs):
        Button.__init__(self, x=x, y=y, label="", size=size, color=color, **kwargs)

    @property
    def right_extent(self):
        return self.x + self.size + self.text_size

    def draw_icon(self):
        pushMatrix()
        x = self.x
        y = self.y
        strokeWeight(2)
        stroke(self.color)
        translate(x, y)
        translate(self.width/2, self.height/2)
        for r in xrange(4):
            rotate(pi/2)
            line(self.size/2, 0, 0, 0)
            pushMatrix()
            translate(self.size/2, 0)
            fill(self.color)
            triangle(0, 0, -4, 2, -4, -2)
            popMatrix()
        popMatrix()


class MagnifyingGlassButton(Button):

    def __init__(self, x, y, size=20, color="#5A5A5A", **kwargs):
        Button.__init__(self, x=x, y=y, label="", size=size, color=color, **kwargs)

    @property
    def right_extent(self):
        return self.x + self.size + self.text_size

    def draw_icon(self):
        pushMatrix()
        x = self.x
        y = self.y
        strokeWeight(2)
        noFill()
        stroke(self.color)
        translate(x, y)
        translate(self.width/2, self.height/2)
        ellipse(0, 0, self.size, self.size)
        pushMatrix()
        rotate(pi / 4)
        translate(self.size / 2, 0)
        line(self.size / 2, 0, 0, 0)
        popMatrix()
        popMatrix()


class MagnifyingGlassMousePointer(object):

    def __init__(self, size=20, color="#5A5A5A"):
        self.size = size
        self.color = color

    def draw(self):
        x = mouseX
        y = mouseY
        strokeWeight(2)
        noFill()
        stroke(self.color)
        ellipse(x, y, self.size, self.size)
        pushMatrix()
        translate(x, y)
        rotate(pi / 4)
        translate(self.size / 2, 0)
        line(self.size / 2, 0, 0, 0)
        popMatrix()
        pushMatrix()
        translate(x, y)
        rotate(pi / 2)
        for r in xrange(2):
            rotate(pi)
            pushMatrix()
            translate(self.size, 0)
            line(self.size / 2, 0, 0, 0)
            translate(self.size / 2, 0)
            triangle(0, 0, -4, 2, -4, -2)
            popMatrix()
        popMatrix()


class MoveMousePointer(object):

    def __init__(self, size=20, color="#5A5A5A"):
        self.size = size
        self.color = color

    def draw(self):
        x = mouseX
        y = mouseY
        strokeWeight(2)
        stroke(self.color)
        pushMatrix()
        translate(x, y)
        for r in xrange(4):
            rotate(pi / 2)
            line(self.size / 2, 0, 0, 0)
            pushMatrix()
            translate(self.size / 2, 0)
            fill(self.color)
            triangle(0, 0, -4, 2, -4, -2)
            popMatrix()
        popMatrix()


class Check(object):

    def __init__(self, x, y, size=20, color="#00833C"):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size / 10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size / 5)
        translate(0, self.size / 4)
        rotate(pi / 6)
        line(-self.size / 4, 0, 0, 0)
        rotate(pi / 2)
        line(-self.size * 0.6, 0, 0, 0)
        popMatrix()


def check(x, y, size=20, color="#00833C"):
    Check(x, y, size, color).draw()


class XMark(object):

    def __init__(self, x, y, size=20, color="#FF5000"):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size / 10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size / 5)
        rotate(pi / 4)
        line(-self.size / 2, 0, self.size / 2, 0)
        rotate(pi / 2)
        line(-self.size / 2, 0, self.size / 2, 0)
        popMatrix()


def x_mark(x, y, size=20, color="#FF5000"):
    XMark(x, y, size, color).draw()


class Square(object):

    def __init__(self, x, y, size, color="#5A5A5A", fill="#B9B9B9"):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.fill = fill

    def draw(self):
        pushMatrix()
        stroke(self.color)
        fill(self.fill)
        translate(self.x, self.y)
        translate(-self.size / 2, -self.size / 2)
        strokeWeight(self.size / 10)
        rect(0, 0, self.size, self.size)
        popMatrix()


def square(x, y, size, color="#5A5A5A", fill="#B9B9B9"):
    Square(x, y, size, color, fill).draw()


class Circle(object):

    def __init__(self, x, y, size, color="#5A5A5A", fill="#B9B9B9"):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.fill = fill

    def draw(self):
        pushMatrix()
        stroke(self.color)
        fill(self.fill)
        translate(self.x, self.y)
        strokeWeight(self.size / 10)
        ellipse(0, 0, self.size, self.size)
        popMatrix()


def circle(x, y, size, color="#5A5A5A", fill="#B9B9B9"):
    Circle(x, y, size, color, fill).draw()
