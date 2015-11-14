
page_height = 768
page_width = 1024

tables = []
application = None


class State(object):

    def name(self):
        return "???"

    def mousePressed(self):
        pass

    def mouseReleased(self):
        pass

    def mouseDragged(self):
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
                 application.state = SelectedTable
            else:
                table.selected = False


ReadyState = _ReadyState()


class _SelectedTable(State):

    def name(self):
        return "Selected " + application.selected_table.name


SelectedTable = _SelectedTable()


class _MoveTable(State):

    def name(self):
        return "Moving"


MoveTable = _MoveTable()


class _NameEdit(State):

    def name(self):
        return "Moving"

NameEdit = _NameEdit()


class Application(object):

    def __init__(self):
        self.state = ReadyState
        self.selected_table = None

    def draw(self):
        fill(255)
        textSize(48)
        text(self.state.name(),
             page_width - 100 - textWidth(self.state.name()),
             page_height - 100)


class Table(object):

    def __init__(self, **kwargs):
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

    def _calculate_width(self):
        textSize(self.text_size)
        width = textWidth(self.name)
        for column in self.columns:
            if width < column._calculate_width():
                width = column._calculate_width()
        return width + 20

    def _calculate_height(self):
        return self.text_size + 30

    def _calculate_full_height(self):
        return sum([self.height] + [x.height for x in self.columns])

    def draw(self):

        fill(self.color)
        self.width = self._calculate_width()
        self.height = self._calculate_height()
        self.height = self.text_size + 30
        rect(self.x, self.y, self.width, self.height)
        fill(self.text_color)
        textSize(self.text_size)
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
        self.name = None
        self.type = None
        self.len = None
        self.ref = None
        self.height = 100
        self.text_size = 24
        self.__dict__.update(kwargs)

    def _calculate_width(self):
        textSize(self.text_size)
        width = textWidth(self.name)
        print width
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
        text(self.name, self.x + 10, self.y + self.text_size + 10)


def setup():
    global tables, application

    application = Application()
    size(page_width, page_height)
    t = Table(name="Gorilla", color="#804000", text_color=255, x=100, y=100)
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
