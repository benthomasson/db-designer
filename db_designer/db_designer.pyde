

import os
import yaml
import traceback

page_height = 768
page_width = 1024

TEXT_SIZE = 18

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

    def mouse_select(self):

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
        if application.selected_table:
            table = application.selected_table
            for column in table.columns:
                if (mouseX > column.left_extent and
                    mouseX < column.right_extent and
                    mouseY > column.top_extent and
                    mouseY < column.bottom_extent):
                     application.editing_column = column
                     application.changeState(ColumnEdit)
        if application.selected_table is None:
            application.changeState(MenuWheel)



class _ReadyState(State):

    def name(self):
        return "Ready"

    def mousePressed(self):
        application.selected_table = None
        self.mouse_select()

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
        elif menu_selection == "Load":
            application.changeState(Load)
        else:
            application.changeState(ReadyState)

MenuWheel = _MenuWheel()

class _Load(State):

    def name(self):
        return "Loading from file"

    def start(self):
        selectInput("Input file", "fileSelected")

    def fileSelected(self, selection):
        global tables
        try:
            print selection, type(selection)
            if selection:
                new_tables = []
                with open(selection.getAbsolutePath()) as f:
                    d = yaml.load(f.read())
                    print d
                for model in d.get('models'):
                    table = Table(name=model.get('name'),
                                  x=model.get('x', 0),
                                  y=model.get('y', 0))
                    new_tables.append(table)
                    for field in model.get('fields'):
                        name = field.get('name')
                        ftype = field.get('type')
                        flen = field.get('len')
                        column = Column(name=":".join(map(str, filter(None, [name, ftype, flen]))),
                                        x=model.get('x', 0),
                                        y=model.get('y', 0),
                                        table=table)
                        table.columns.append(column)
                for model in d.get('models'):
                    ts = [t for t in new_tables if t.name == model.get('name')]
                    assert len(ts) == 1
                    from_table = ts[0]
                    for field in model.get('fields'):
                        if field.get('ref') and field.get('ref_field'):
                            cs = [c for c in from_table.columns if c.name.partition(":")[0] == field.get('name')]
                            assert len(cs) == 1
                            from_column = cs[0]
                            ts = [t for t in new_tables if t.name == field.get('ref')]
                            assert len(ts) == 1
                            to_table = ts[0]
                            cs = [c for c in to_table.columns if c.name.partition(":")[0] == field.get('ref_field')]
                            assert len(cs) == 1
                            to_column = cs[0]
                            from_column.connectors = [ForeignKey(from_column=from_column, to_column=to_column)]
                        elif field.get('ref'):
                            cs = [c for c in from_table.columns if c.name.partition(":")[0] == field.get('name')]
                            if len(cs) == 1:
                                from_column = cs[0]
                                ts = [t for t in new_tables if t.name == field.get('ref')]
                                if len(ts) == 0:
                                    to_column = Column(name='pk')
                                    to_table = Table(name=field.get('ref'), columns=[to_column])
                                    to_column.table = to_table
                                    new_tables.append(to_table)
                                    from_column.connectors = [ForeignKey(from_column=from_column, to_column=to_column)]
                                elif len(ts) == 1:
                                    to_table = ts[0]
                                    to_column = to_table.columns[0]
                                    from_column.connectors = [ForeignKey(from_column=from_column, to_column=to_column)]
                                else:
                                    print "When connecting {0}.{1} expected one table named {2} found {3}".format(from_table.name, from_column.name, field.get('ref'), ts)
                            else:
                                print "When connecting {0}.{1} expected one column named {2} found {3}".format(from_table.name, field.get('name'), field.get('name'), cs)
                tables = new_tables
            print "Read from {0}".format(selection)
            application.changeState(ReadyState)
        except Exception:
            print traceback.format_exc()


Load = _Load()


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

    def start(self):
        if application.selected_table:
            application.selected_table.delete_empty_columns()
            application.selected_table.add_empty_column()

    def end(self):
        if application.selected_table:
            application.selected_table.delete_empty_columns()

    def mousePressed(self):
        table = application.selected_table
        if not (mouseX > table.left_extent and
                mouseX < table.right_extent and
                mouseY > table.top_extent and
                mouseY < table.bottom_extent):
            self.end()
            table.selected = False
            application.selected_table = None
            self.mouse_select()
            return
        if (mouseX > table.left_title_extent and
            mouseX < table.right_title_extent and
            mouseY > table.top_title_extent and
            mouseY < table.bottom_title_extent):
            application.changeState(NameEdit)
            return

        for column in table.columns:
            if (mouseX > column.left_extent and
                mouseX < column.right_extent and
                mouseY > column.top_extent and
                mouseY < column.bottom_extent):
                 application.editing_column = column
                 application.changeState(ColumnEdit)
                 return


    def mouseDragged(self):
        application.changeState(MoveTable)


    def keyTyped(self):
        if key == DELETE or key == BACKSPACE:
            application.selected_table.selected = False
            tables.remove(application.selected_table)
            application.changeState(ReadyState)


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

    def start(self):
        if application.selected_table:
            application.selected_table.edit = True

    def end(self):
        if application.selected_table:
            application.selected_table.edit = False

    def mousePressed(self):
        table = application.selected_table
        if not (mouseX > table.left_title_extent and
                mouseX < table.right_title_extent and
                mouseY > table.top_title_extent and
                mouseY < table.bottom_title_extent):
            application.selected_table.edit = False
            application.selected_table = None
            self.mouse_select()

    def mouseDragged(self):
        application.changeState(MoveTable)

    def keyTyped(self):
        if key == RETURN:
            application.changeState(SelectedTable)
        elif key == ENTER:
            application.changeState(SelectedTable)
        elif key == BACKSPACE:
            application.selected_table.name = application.selected_table.name[:-1]
        elif key == DELETE:
            application.selected_table.name = application.selected_table.name[:-1]
        else:
            application.selected_table.name += key

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
            self.end()
            application.selected_table = None
            self.mouse_select()

    def start(self):
        application.editing_column.edit = True

    def end(self):
        if application.editing_column:
            application.editing_column.edit = False
            application.editing_column = None
        if application.selected_table:
            application.selected_table.delete_empty_columns()

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
        application.connecting_column = application.editing_column
        application.connecting_connector = ForeignKey(from_column=application.connecting_column,
                                                      connecting=True)
        application.connecting_column.connectors = [application.connecting_connector]
        application.changeState(Connect)

ColumnEdit = _ColumnEdit()

class _Connect(State):

    def name(self):
        return "Connecting {0}".format(application.connecting_column.name)

    def end(self):
        if (application.connecting_connector and
            application.connecting_connector.to_column is None):
                application.connecting_column.connectors.remove(application.connecting_connector)
        application.connecting_connector = None
        application.connecting_column = None

    def mouseReleased(self):
        for table in tables:
            for column in table.columns:
                if (mouseX > column.left_extent and
                    mouseX < column.right_extent and
                    mouseY > column.top_extent and
                    mouseY < column.bottom_extent):
                     application.connecting_connector.to_column = column
                     break
        application.changeState(ReadyState)

Connect = _Connect()

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


    def draw(self):
        if self.x and self.y:
            noFill()
            stroke(0)
            strokeWeight(2)
            ellipse(self.x, self.y, 100, 100)
            textSize(TEXT_SIZE)
            text("New", self.x - 55, self.y - 55)
            text("Save", self.x + 55, self.y + 55 + TEXT_SIZE)
            text("Load", self.x + 55, self.y - 55)
            line(self.x, self.y, self.x + 50, self.y)
            line(self.x, self.y, self.x - 50, self.y)
            line(self.x, self.y, self.x, self.y - 50)
            line(self.x, self.y, self.x, self.y + 50)
            line(self.x, self.y, mouseX, mouseY)


class Application(object):

    def __init__(self):
        self.state = ReadyState
        self.selected_table = None
        self.editing_column = None
        self.connecting_column = None
        self.connecting_connector = None
        self.wheel = None

    def changeState(self, state):
        if self.state:
            self.state.end()
        self.state = state
        if self.state:
            self.state.start()

    def draw(self):
        fill(255)
        textSize(TEXT_SIZE)
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
        self.color = 200
        self.text_color = 0
        self.text_size = TEXT_SIZE
        self.name = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.full_height = 0
        self.__dict__.update(kwargs)

    def add_empty_column(self):
        if all([c.name for c in self.columns]):
            self.columns.append(Column(table=self))

    def delete_empty_columns(self):
        for c in self.columns[:-1]:
            if not c.name and c.edit is False:
                self.columns.remove(c)

    def to_dict(self):
        d = {}
        d['name'] = self.name
        d['fields'] = fields = []
        d['x'] = self.x
        d['y'] = self.y
        for column in self.columns:
            if column.name:
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
            strokeWeight(2)
            noFill()
            stroke("#66FFFF")
            rect(self.x, self.y, self.width, self.full_height)
            strokeWeight(1)
            stroke(0)

    @property
    def left_title_extent(self):
        return self.x

    @property
    def right_title_extent(self):
        return self.x + self.width

    @property
    def top_title_extent(self):
        return self.y

    @property
    def bottom_title_extent(self):
        return self.y + self.height

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
        self.table = None
        self.connectors = []
        self.x = 0
        self.y = 0
        self.edit = False
        self.name = ""
        self.ref = None
        self.width = 100
        self.height = 100
        self.text_size = TEXT_SIZE
        self.__dict__.update(kwargs)

    def to_dict(self):
        d = {}
        d['name'], _, rest = self.name.partition(":")
        if rest:
            d['type'], _, rest = rest.partition(":")
        if rest:
            try:
                d['len'], _, rest = rest.partition(":")
                d['len'] = int(d['len'])
            except ValueError:
                pass
        if self.connectors:
            d['ref'] = self.connectors[0].to_column.table.name
            d['ref_field'] = self.connectors[0].to_column.name.partition(":")[0]
        d['x'] = self.x
        d['y'] = self.y
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
        strokeWeight(1)
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


class ForeignKey(object):

    def __init__(self, **kwargs):
        self.connecting = False
        self.from_column = None
        self.to_column = None
        self.__dict__.update(kwargs)

    def draw(self):
        if self.from_column and self.to_column:
            y1 = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            y2 = (self.to_column.top_extent + self.to_column.bottom_extent) / 2
            if self.from_column.right_extent < self.to_column.left_extent:
                x1 = self.from_column.right_extent
                x2 = self.to_column.left_extent
            elif self.from_column.left_extent > self.to_column.right_extent:
                x1 = self.from_column.left_extent
                x2 = self.to_column.right_extent
            else:
                x1 = (self.from_column.right_extent + self.from_column.left_extent) / 2
                x2 = (self.to_column.right_extent + self.to_column.left_extent) / 2
            strokeWeight(2)
            line(x1, y1, x2, y2)
        elif self.from_column and self.connecting:
            if mouseX > self.from_column.right_extent:
                x = self.from_column.right_extent
                y = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            elif mouseX < self.from_column.left_extent:
                x = self.from_column.left_extent
                y = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            else:
                x = (self.from_column.right_extent + self.from_column.left_extent) / 2
                y = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            strokeWeight(2)
            line(x, y, mouseX, mouseY)


def setup():
    global tables, application
    frameRate(30)
    size(page_width, page_height, FX2D)

    #textFont(createFont("Courier", TEXT_SIZE, True))

    application = Application()


def draw():
    fill(126)
    rect(0,0, page_width, page_height)
    application.draw()
    for table in tables:
        for column in table.columns:
            for connector in column.connectors:
                connector.draw()
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
