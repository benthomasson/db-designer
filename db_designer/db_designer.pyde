

import os
import yaml
import traceback

page_height = 768
page_width = 1024

tables = []
application = None


class State(object):

    def name(self):
        return "???"

    def start(self):
        pass

    def end(self):
        pass

    def mousePressed(self):
        pass

    def mouseReleased(self):
        pass

    def mouseDragged(self):
        pass

    def keyPressed(self):
        pass

    def keyReleased(self):
        pass

    def keyTyped(self):
        pass

    def fileSelected(self, selected):
        pass

class _ReadyState(State):

    def name(self):
        return "Ready"

    def mousePressed(self):
        application.selected_table = None
        for table in tables:
            if (mouseX > table.left_extent and
                mouseX < table.right_extent and
                mouseY > table.top_extent and
                mouseY < table.bottom_extent):
                 application.selected_table = table
                 table.selected = True
                 application.changeState(SelectedTable)
            else:
                table.selected = False

        if application.selected_table is None:
            application.changeState(MenuWheel)

    def mouseDragged(self):
        application.changeState(MenuWheel)

ReadyState = _ReadyState()

class _MenuWheel(State):

    def name(self):
        return "Menu Wheel"

    def start(self):
        application.wheel = Wheel(mouseX, mouseY)

    def end(self):
        application.wheel = None

    def mouseReleased(self):
        menu_selection = application.wheel.get_menu_selection()
        if menu_selection == "New":
            application.changeState(NewTable)
        elif menu_selection == "Save":
            application.changeState(Save)
        else:
            application.changeState(ReadyState)

MenuWheel = _MenuWheel()

class _Save(State):

    def name(self):
        return "Save"

    def start(self):
        selectOutput("Output file", "fileSelected")

    def fileSelected(self, selection):
        try:
            print selection, type(selection)
            if selection:
                app = {}
                app['app'] = os.path.splitext(os.path.basename(selection.getAbsolutePath()))[0]
                app['models'] = [t.to_dict() for t in tables]
                with open(selection.getAbsolutePath(), 'w') as f:
                    f.write(yaml.safe_dump(app, default_flow_style=False))
            print "Wrote to {0}".format(selection)
            application.changeState(ReadyState)
        except Exception:
            print traceback.format_exc()

Save = _Save()

class _SelectedTable(State):

    def name(self):
        return "Selected " + application.selected_table.name

    def mousePressed(self):
        table = application.selected_table
        if not (mouseX > table.left_extent and
                mouseX < table.right_extent and
                mouseY > table.top_extent and
                mouseY < table.bottom_extent):
            table.selected = False
            application.changeState(ReadyState)
        for column in table.columns:
            if (mouseX > column.left_extent and
                mouseX < column.right_extent and
                mouseY > column.top_extent and
                mouseY < column.bottom_extent):
                 application.editing_column = column
                 application.changeState(ColumnEdit)

    def mouseDragged(self):
        application.changeState(MoveTable)

SelectedTable = _SelectedTable()


class _NewTable(State):

    def name(self):
        return "New Table!"

    def start(self):
        t = Table(name="New", x=mouseX, y=mouseY)
        tables.append(t)
        application.changeState(ReadyState)

NewTable = _NewTable()


class _MoveTable(State):

    def name(self):
        return "Moving table {0}".format(application.selected_table.name)

    def start(self):
         application.diffX = mouseX - application.selected_table.x
         application.diffY = mouseY - application.selected_table.y


    def mouseDragged(self):
        if application.selected_table:
            application.selected_table.x = mouseX - application.diffX
            application.selected_table.y = mouseY - application.diffY

    def mouseReleased(self):
        application.changeState(SelectedTable)

MoveTable = _MoveTable()


class _NameEdit(State):

    def name(self):
        return "Editing {0}".format(application.selected_table.name)

NameEdit = _NameEdit()

class _ColumnEdit(State):

    def name(self):
        return "Editing {0} {1}".format(application.selected_table.name,
                                        application.editing_column.name)
    def mousePressed(self):
        column = application.editing_column
        if not (mouseX > column.left_extent and
                mouseX < column.right_extent and
                mouseY > column.top_extent and
                mouseY < column.bottom_extent):
            application.changeState(SelectedTable)

    def start(self):
        application.editing_column.edit = True

    def end(self):
        application.editing_column.edit = False
        application.editing_column = None

    def keyTyped(self):
        if key == RETURN:
            application.changeState(SelectedTable)
        elif key == ENTER:
            application.changeState(SelectedTable)
        elif key == BACKSPACE:
            application.editing_column.name = application.editing_column.name[:-1]
        elif key == DELETE:
            application.editing_column.name = application.editing_column.name[:-1]
        else:
            application.editing_column.name += key

    def mouseDragged(self):
        application.changeState(MoveTable)

ColumnEdit = _ColumnEdit()


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
            return "Bar"
        elif mouseX < self.x and mouseY > self.y:
            return "Foo"
        return None


    def draw(self):
        if self.x and self.y:
            noFill()
            stroke(0)
            strokeWeight(2)
            ellipse(self.x, self.y, 100, 100)
            textSize(24)
            text("New", self.x - 55, self.y - 55)
            text("Save", self.x + 55, self.y + 55 + 24)
            text("Foo", self.x - 55 - textWidth("Foo"), self.y + 55)
            text("Bar", self.x + 55, self.y - 55)
            line(self.x, self.y, self.x + 50, self.y)
            line(self.x, self.y, self.x - 50, self.y)
            line(self.x, self.y, self.x, self.y - 50)
            line(self.x, self.y, self.x, self.y + 50)
            line(self.x, self.y, mouseX, mouseY)


class Application(object):

    def __init__(self):
        self.state = ReadyState
        self.selected_table = None
        self.wheel = None

    def changeState(self, state):
        if self.state:
            self.state.end()
        self.state = state
        if self.state:
            self.state.start()

    def draw(self):
        fill(255)
        textSize(48)
        text(self.state.name(),
             page_width - 100 - textWidth(self.state.name()),
             page_height - 100)
        fps = "fps: {0}".format(int(frameRate))
        text(fps,
             page_width - 100 - textWidth(fps),
             page_height - 50)
        if self.wheel:
            self.wheel.draw()


class Table(object):

    def __init__(self, **kwargs):
        self.edit = False
        self.selected = False
        self.columns = []
        self.color = 255
        self.text_color = 0
        self.text_size = 48
        self.name = None
        self.x = None
        self.y = None
        self.width = 0
        self.height = 0
        self.full_height = 0
        self.__dict__.update(kwargs)

    def to_dict(self):
        d = {}
        d['name'] = self.name
        d['fields'] = fields = []
        for column in self.columns:
            fields.append(column.to_dict())
        return d

    def _calculate_width(self):
        textSize(self.text_size)
        width = textWidth(self.name)
        if self.edit:
            width += 1
        for column in self.columns:
            if width < column._calculate_width():
                width = column._calculate_width()
        return width + 20

    def _calculate_height(self):
        return self.text_size + 30

    def _calculate_full_height(self):
        return sum([self.height] + [x.height for x in self.columns])

    def draw(self):

        stroke(0)
        strokeWeight(1)
        fill(self.color)
        self.width = self._calculate_width()
        self.height = self._calculate_height()
        self.height = self.text_size + 30
        rect(self.x, self.y, self.width, self.height)
        fill(self.text_color)
        textSize(self.text_size)
        if self.edit:
            text(self.name + "_", self.x + 10, self.y + self.text_size + 10)
        else:
            text(self.name, self.x + 10, self.y + self.text_size + 10)

        previous_column = None
        for column in self.columns:
            column.draw(self, previous_column)
            previous_column = column

        self.full_height = self._calculate_full_height()

        if self.selected:
            strokeWeight(5)
            noFill()
            stroke("#66FFFF")
            rect(self.x, self.y, self.width, self.full_height)
            strokeWeight(1)
            stroke(0)

    @property
    def left_extent(self):
        return self.x

    @property
    def right_extent(self):
        return self.x + self.width

    @property
    def top_extent(self):
        return self.y

    @property
    def bottom_extent(self):
        return self.y + self.full_height

class Column(object):

    def __init__(self, **kwargs):
        self.edit = False
        self.name = None
        self.type = None
        self.len = None
        self.ref = None
        self.width = 100
        self.height = 100
        self.text_size = 24
        self.__dict__.update(kwargs)

    def to_dict(self):
        d = {}
        d['name'] = self.name
        return d

    def _calculate_width(self):
        textSize(self.text_size)
        width = textWidth(self.name)
        if self.edit:
            width += 1
        return width

    def draw(self, table, previous_column):
        if previous_column is None:
            self.x = table.x
            self.y = table.y + table.height
        else:
            self.x = table.x
            self.y = previous_column.y + previous_column.height
        self.width = table.width
        self.height = self.text_size + 30
        textSize(self.text_size)
        fill(255)
        rect(self.x, self.y, self.width, self.height)
        fill(0)
        if self.edit:
            text(self.name + "_", self.x + 10, self.y + self.text_size + 10)
        else:
            text(self.name, self.x + 10, self.y + self.text_size + 10)

    @property
    def left_extent(self):
        return self.x

    @property
    def right_extent(self):
        return self.x + self.width

    @property
    def top_extent(self):
        return self.y

    @property
    def bottom_extent(self):
        return self.y + self.height


def setup():
    global tables, application

    application = Application()
    size(page_width, page_height)
    t = Table(name="Gorilla",
              color="#804000",
              text_color=255,
              x=100,
              y=100)
    t.columns.append(Column(name="name"))
    t.columns.append(Column(name="is_alive_and_still_kicking"))
    tables.append(t)


def draw():
    fill(126)
    rect(0,0, page_width, page_height)
    application.draw()
    for table in tables:
        table.draw()


def mousePressed():
    application.state.mousePressed()


def mouseDragged():
    application.state.mouseDragged()


def mouseReleased():
    application.state.mouseReleased()


def keyPressed():
    application.state.keyPressed()


def keyReleased():
    application.state.keyReleased()

def keyTyped():
    application.state.keyTyped()

def fileSelected(selection):
    application.state.fileSelected(selection)
