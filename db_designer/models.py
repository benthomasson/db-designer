

from conf import settings as my_settings

from widgets import arrow
from processing_widgets.widgets import Button, ButtonBar
import os
from subprocess import Popen, PIPE


class Application(object):

    def __init__(self):
        self.app_name = "DB Designer"
        self.state = None
        self.selected_table = None
        self.editing_column = None
        self.connecting_column = None
        self.connecting_connector = None
        self.wheel = None
        self.panX = 0
        self.panY = 0
        self.mousePX = 0
        self.mousePY = 0
        self.scaleXY = 1
        self.oldPanY = 0
        self.oldPanX = 0
        self.oldScaleXY = 1
        self.mousePressedX = 0
        self.mousePressedY = 0
        self.lastKeyCode = 0
        self.debug = False
        self.tables = []
        self.modules = []
        self.api = None
        self.generate = None
        self.directory = None
        self.mouse_pointer = None
        self.active_widgets = []
        self.active_widgets.append(Button(x=0, y=0, label="Save", call_back=self.save))
        self.active_widgets.append(Button(x=0, y=0, label="Load", call_back=self.load))
        self.active_widgets.append(Button(x=0, y=0, label="Generate", call_back=self.generate_button))
        self.button_bar = ButtonBar(self.active_widgets, 10, 10)

    def save(self, button):
        from db_designer_fsm import Save
        self.changeState(Save)

    def load(self, button):
        from db_designer_fsm import Load
        self.changeState(Load)

    def generate_button(self, button):
        p = Popen(self.generate, shell=True, cwd=self.directory, stdout=PIPE)
        stdout, stderr = p.communicate()
        print stderr
        print stdout

    def changeState(self, state):
        if self.state:
            self.state.end(self)
        self.state = state
        if self.state:
            self.state.start(self)

    def draw(self, controller):
        if self.debug:
            fill(my_settings.COLOR)
            textSize(my_settings.TEXT_SIZE)
            text(self.state.name(),
                 width - 100 - textWidth(self.state.name()),
                 height - 100)
            fps = "fps: {0}".format(int(frameRate))
            text(fps,
                 width - 100 - textWidth(fps),
                 height - 50)
            try:
                key_t = ""
                key_t = "key: {0} keyCode: {1}".format(str(key).strip(), keyCode)
            except Exception:
                pass
            text(key_t,
                 width - 100 - textWidth(key_t),
                 height - 70)
            mouseButton_t = "mouseButton: {0}".format(mouseButton)
            text(mouseButton_t,
                 width - 100 - textWidth(mouseButton_t),
                 height - 90)

        if self.wheel:
            self.wheel.draw(controller)

        self.button_bar.draw()

        if self.mouse_pointer:
            self.mouse_pointer.draw()


class Table(object):

    def __init__(self, **kwargs):
        self.edit = False
        self.selected = False
        self.columns = []
        self.color = 200
        self.text_size = my_settings.TEXT_SIZE
        self.name = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.full_height = 0
        self.external = False
        self.extra = False
        self.view = False
        self.natural_key = None
        self.natural_keys = []
        self.display = None
        self.ordering = []
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "Table(name={0})".format(self.name)

    def is_selected(self, controller):
        return (controller.mousePX > self.left_extent and
                controller.mousePX < self.right_extent and
                controller.mousePY > self.top_extent and
                controller.mousePY < self.bottom_extent)

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
        d['x'] = int(self.x)
        d['y'] = int(self.y)
        if self.extra:
            d['extra'] = self.extra
        if self.view:
            d['view'] = self.view
        if self.natural_key:
            d['natural_key'] = self.natural_key
        if self.display:
            d['display'] = self.display
        if self.natural_keys:
            d['natural_keys'] = self.natural_keys
        if self.ordering:
            d['ordering'] = self.ordering
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

    def draw(self, controller):

        stroke(0)
        strokeWeight(1)
        fill(self.color)
        self.width = self._calculate_width()
        self.height = self._calculate_height()
        self.height = self.text_size + 30
        rect(self.x, self.y, self.width, self.height)
        fill(my_settings.COLOR)
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
        self.pk = False
        self.related_name = None
        self.text_size = my_settings.TEXT_SIZE
        self.__dict__.update(kwargs)

    def is_selected(self, controller):
        return (controller.mousePX > self.left_extent and
                controller.mousePX < self.right_extent and
                controller.mousePY > self.top_extent and
                controller.mousePY < self.bottom_extent)

    def to_dict(self):
        d = {}
        if self.pk:
            d['pk'] = self.pk
        if self.related_name is not None:
            d['related_name'] = self.related_name
        d['name'], _, rest = self.name.partition(":")
        if rest:
            d['type'], _, rest = rest.partition(":")
            if d['type'] == "AutoField":
                d['pk'] = True
        if rest:
            try:
                length, _, rest = rest.partition(":")
                d['len'] = int(length)
            except ValueError:
                if length == "False" or length == "false":
                    d['default'] = False
                elif length == "True" or length == "true":
                    d['default'] = true

        if self.connectors and d.get('type') == "ForeignKey":
            d['ref'] = self.connectors[0].to_column.table.name
            d['ref_field'] = self.connectors[0].to_column.name.partition(":")[0]
        if d['name'].endswith("_id") and d.get('type') == "ForeignKey":
            d['name'] = d['name'][:-3]
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
        stroke(my_settings.COLOR)
        rect(self.x, self.y, self.width, self.height)
        fill(my_settings.COLOR)
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

    def draw(self, controller):
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
            arrow(x1, y1, x2, y2)
        elif self.from_column and self.connecting:
            if controller.mousePX > self.from_column.right_extent:
                x = self.from_column.right_extent
                y = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            elif controller.mousePX < self.from_column.left_extent:
                x = self.from_column.left_extent
                y = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            else:
                x = (self.from_column.right_extent + self.from_column.left_extent) / 2
                y = (self.from_column.top_extent + self.from_column.bottom_extent) / 2
            strokeWeight(2)
            arrow(x, y, controller.mousePX, controller.mousePY)
