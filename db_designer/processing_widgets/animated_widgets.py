

from math import pi, sqrt, atan2


class Animated(object):

    @property
    def frameSpeed(self):
        return round(frameRate)/self.speed

    @property
    def phasePercent(self):
        return 1.0 * (self.frame - self.frameSpeed * self.phase) / self.frameSpeed

    def draw(self):
        if self.frame < self.max_phase * self.frameSpeed:
            phase = getattr(self, "phase{0}".format(int(self.frame/self.frameSpeed)))
            phase()
            self.frame += 1
        else:
            self.final_phase()


class Check(Animated):

    def __init__(self, x, y, size=20, color="#00833C", speed=3):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.frame = 0
        self.phase = 0
        self.max_phase = 3

    def phase0(self):
        self.phase = 0
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        arc(0, 0, self.size, self.size, pi*3/2, pi*3/2 + 2 * pi * self.phasePercent)
        popMatrix()

    def phase1(self):
        self.phase = 1
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size/5)
        translate(0, self.size/4)
        rotate(pi/6)
        line(-self.size/4, 0, -self.size/4 * (1 - self.phasePercent), 0)
        popMatrix()

    def phase2(self):
        self.phase = 2
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size/5)
        translate(0, self.size/4)
        rotate(pi/6)
        line(-self.size/4, 0, 0, 0)
        rotate(pi/2)
        line(-self.size * 0.6 * self.phasePercent, 0, 0, 0)
        popMatrix()

    def final_phase(self):
        self.phase = 3
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size/5)
        translate(0, self.size/4)
        rotate(pi/6)
        line(-self.size/4, 0, 0, 0)
        rotate(pi/2)
        line(-self.size * 0.6, 0, 0, 0)
        popMatrix()


def check(x, y, size=20, color="#00833C"):
    Check(x, y, size, color).draw()


class XMark(Animated):

    def __init__(self, x, y, size=20, color="#FF5000", speed=3):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.frame = 0
        self.phase = 0
        self.max_phase = 3

    def phase0(self):
        self.phase = 0
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        arc(0, 0, self.size, self.size, pi*3/2, pi*3/2 + 2 * pi * self.phasePercent)
        popMatrix()

    def phase1(self):
        self.phase = 1
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size/5)
        rotate(pi/4)
        translate(-self.size/2, 0)
        line(0, 0, self.size * self.phasePercent, 0)
        popMatrix()

    def phase2(self):
        self.phase = 2
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size/5)
        rotate(pi/4)
        line(-self.size/2, 0, self.size/2, 0)
        rotate(pi/2)
        translate(-self.size/2, 0)
        line(0, 0, self.size * self.phasePercent, 0)
        popMatrix()

    def final_phase(self):
        pushMatrix()
        stroke(self.color)
        fill(255)
        translate(self.x, self.y)
        strokeWeight(self.size/10)
        ellipse(0, 0, self.size, self.size)
        strokeWeight(self.size/5)
        rotate(pi/4)
        line(-self.size/2, 0, self.size/2, 0)
        rotate(pi/2)
        line(-self.size/2, 0, self.size/2, 0)
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
        translate(-self.size/2, -self.size/2)
        strokeWeight(self.size/10)
        rect(0, 0, self.size, self.size)
        popMatrix()


def square(x, y, size, color="#5A5A5A", fill="#B9B9B9"):
    Square(x, y, size, color, fill).draw()


def normalize(data):
    if max(data) == min(data):
        return data
    return [float(x-min(data))/(max(data)-min(data)) for x in data]


class SparkLine(Animated):

    def __init__(self, label, units, data, x, y, size, color="#B1E3E3", fill="#B1E3E3", speed=1):
        self.label = label
        self.data = data
        self.units = units
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.fill = fill
        self.speed = speed
        self.frame = 0

    @property
    def frameSpeed(self):
        return round(frameRate)/self.speed

    @property
    def phase(self):
        return int(self.frame/self.frameSpeed)

    @property
    def phasePercent(self):
        return 1.0 * (self.frame - self.frameSpeed * self.phase) / self.frameSpeed

    def draw(self):
        if self.frame < 9 * self.frameSpeed and self.frame < (len(self.data) - 1) * self.frameSpeed:
            self.startup_phase()
            self.frame += 1
        elif self.frame < (len(self.data) - 1) * self.frameSpeed:
            self.extending_phase()
            self.frame += 1
        else:
            self.final_phase()

    def _draw_label(self):
        stroke(self.color)
        fill(self.fill)
        translate(self.x, self.y)
        translate(-self.size/2, -self.size/2)
        textSize(self.size)
        text(self.label, 0, self.size)

    def startup_phase(self):
        strokeWeight(min(2, self.size/10))
        pushMatrix()
        self._draw_label()
        translate(textWidth(self.label) + self.size/8, self.size)
        normalized = list(enumerate(normalize(self.data)))
        normalized = normalized[:self.phase + 2]
        previous_datum = normalized[0]
        for datum in normalized[1:-1]:
            x1, y1 = previous_datum
            x2, y2 = datum
            line(x1*self.size/2, -y1*self.size, x2*self.size/2, -y2*self.size)
            previous_datum = datum

        if len(normalized) >= 2:
            px, py = normalized[-2]
            x, y = normalized[-1]
            pushMatrix()
            translate(px*self.size/2, -py*self.size)
            x1 = px*self.size/2
            x2 = x*self.size/2
            y1 = -py*self.size
            y2 = -y*self.size
            rotate(atan2(y2-y1, x2-x1))
            line(0, 0, sqrt((y2-y1)**2 + (x2-x1)**2) * self.phasePercent, 0)
            translate(sqrt((y2-y1)**2 + (x2-x1)**2) * self.phasePercent, 0)
            ellipse(0, 0, self.size/4, self.size/4)
            popMatrix()
            translate(self.size/2*(min(10, len(normalized)) - 1.5) + self.size/2 * self.phasePercent, 0)
            current_datum = self.data[self.phase+1]
            text("{0}{1}".format(current_datum, self.units), 0, 0)
        else:
            x, y = normalized[-1]
            ellipse(x*self.size/2, -y*self.size, self.size/4, self.size/4)
            translate(self.size/2*(min(10, len(normalized)) - 0.5), 0)
            text("{0}{1}".format(self.data[self.phase], self.units), 0, 0)
        popMatrix()

    def extending_phase(self):
        pushMatrix()
        strokeWeight(min(2, self.size/10))
        self._draw_label()
        translate(textWidth(self.label) + self.size/8, self.size)
        translate(-self.size/2 * self.phasePercent, 0)
        normalized = normalize(self.data)
        normalized = list(enumerate(normalized[self.phase-9:self.phase + 2]))
        off_chart_datum = normalized[0]
        previous_datum = normalized[1]
        px, py = off_chart_datum
        x, y = previous_datum
        pushMatrix()
        translate(x*self.size/2, -y*self.size)
        x1 = x*self.size/2
        x2 = px*self.size/2
        y1 = -y*self.size
        y2 = -py*self.size
        rotate(atan2(y2-y1, x2-x1))
        line(0, 0, sqrt((y2-y1)**2 + (x2-x1)**2) * (1 - self.phasePercent), 0)
        popMatrix()
        for datum in normalized[2:-1]:
            x1, y1 = previous_datum
            x2, y2 = datum
            line(x1*self.size/2, -y1*self.size, x2*self.size/2, -y2*self.size)
            previous_datum = datum

        if len(normalized) >= 2:
            px, py = normalized[-2]
            x, y = normalized[-1]
            pushMatrix()
            translate(px*self.size/2, -py*self.size)
            x1 = px*self.size/2
            x2 = x*self.size/2
            y1 = -py*self.size
            y2 = -y*self.size
            rotate(atan2(y2-y1, x2-x1))
            line(0, 0, sqrt((y2-y1)**2 + (x2-x1)**2) * self.phasePercent, 0)
            translate(sqrt((y2-y1)**2 + (x2-x1)**2) * self.phasePercent, 0)
            ellipse(0, 0, self.size/4, self.size/4)
            popMatrix()
            translate(self.size/2*(min(10, len(normalized)) - 0.5) + self.size/2 * self.phasePercent, 0)
            current_datum = self.data[self.phase+1]
            text("{0}{1}".format(current_datum, self.units), 0, 0)
        else:
            x, y = normalized[-1]
            ellipse(x*self.size/2, -y*self.size, self.size/4, self.size/4)
            translate(self.size/2*(min(10, len(normalized)) - 0.5), 0)
            text("{0}{1}".format(self.data[self.phase], self.units), 0, 0)
        popMatrix()

    def final_phase(self):
        if len(self.data) == 0:
            return
        pushMatrix()
        strokeWeight(min(2, self.size/10))
        self._draw_label()
        translate(textWidth(self.label) + self.size/8, self.size)
        normalized = normalize(self.data)
        normalized = list(enumerate(normalized[-10:]))
        previous_datum = normalized[0]
        x2, y2 = previous_datum
        for datum in normalized[1:10]:
            x1, y1 = previous_datum
            x2, y2 = datum
            line(x1*self.size/2, -y1*self.size, x2*self.size/2, -y2*self.size)
            previous_datum = datum
        ellipse(x2*self.size/2, -y2*self.size, self.size/4, self.size/4)
        fill(self.fill)
        translate(self.size/2*(min(10, len(self.data)) - 0.5), 0)
        text("{0}{1}".format(self.data[-1], self.units), 0, 0)
        popMatrix()
        self.data = self.data[-10:]
        self.frame = (len(self.data) - 1) * self.frameSpeed
