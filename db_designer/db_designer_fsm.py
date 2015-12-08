
import os
import yaml
import traceback
import logging
import random

from models import Table, Column, ForeignKey
from widgets import Wheel


def singleton(klass):
    return klass()


def transition(new_state):
    def called_on(fn):
        transitions = getattr(fn, 'state_transitions', [])
        if isinstance(new_state, basestring):
            transitions.append(new_state)
        elif isinstance(new_state, type):
            transitions.append(new_state.__name__)
        elif isinstance(type(new_state), type):
            transitions.append(new_state.__class__.__name__)
        else:
            raise Exception('Unsupported type {0}'.format(new_state))
        setattr(fn, 'state_transitions', transitions)
        return fn
    return called_on


class State(object):

    def name(self):
        return self.__class__.__name__

    def start(self, controller):
        pass

    def end(self, controller):
        pass

    def mousePressed(self, controller):
        pass

    def mouseReleased(self, controller):
        pass

    def mouseDragged(self, controller):
        pass

    def keyPressed(self, controller):
        pass

    def keyReleased(self, controller):
        pass

    def keyTyped(self, controller):
        pass

    def fileSelected(self, controller, selected):
        pass


@singleton
class Start(State):

    @transition('ReadyState')
    def start(self, controller):
        controller.changeState(ReadyState)


@singleton
class MouseSelect(State):

    @transition('SelectedTable')
    @transition('ColumnEdit')
    @transition('MenuWheel')
    @transition('ReadyState')
    @transition('ScaleAndPan')
    def start(self, controller):

        changed_state = False

        if mouseButton == LEFT:
            for table in controller.tables:
                if table.is_selected(controller):
                    controller.selected_table = table
                    table.selected = True
                    controller.changeState(SelectedTable)
                    changed_state = True
                else:
                    table.selected = False
            if controller.selected_table:
                table = controller.selected_table
                for column in table.columns:
                    if column.is_selected(controller):
                        controller.editing_column = column
                        controller.changeState(ColumnEdit)
                        changed_state = True
        elif controller.selected_table is None and mouseButton == RIGHT:
            controller.changeState(MenuWheel)
            changed_state = True

        if changed_state is False and mouseButton == LEFT:
            controller.changeState(ScaleAndPan)

        if changed_state is False and mouseButton == RIGHT:
            controller.changeState(ReadyState)


@singleton
class ReadyState(State):

    @transition('MouseSelect')
    def mousePressed(self, controller):
        controller.mousePressedX = controller.mousePX
        controller.mousePressedY = controller.mousePY
        controller.selected_table = None
        controller.changeState(MouseSelect)

    @transition('MenuWheel')
    def mouseDragged(self, controller):
        if mouseButton == RIGHT or keyCode == CONTROL:
            controller.changeState(MenuWheel)

    def keyTyped(self, controller):
        if key == CODED:
            pass
        elif key == "d":
            controller.debug = not controller.debug


@singleton
class ScaleAndPan(State):

    def start(self, controller):
        controller.mousePressedX = mouseX
        controller.mousePressedY = mouseY
        controller.oldPanX = controller.panX
        controller.oldPanY = controller.panY
        controller.oldScaleXY = controller.scaleXY

    def mouseDragged(self, controller):
        if mouseButton == LEFT and controller.lastKeyCode == ALT:
            controller.scaleXY = max(0.1, (mouseY - controller.mousePressedY) / 100.0 + controller.oldScaleXY)
            controller.panX = controller.oldPanX + (-1 * controller.mousePressedX / controller.oldScaleXY) + (controller.mousePressedX / controller.scaleXY)
            controller.panY = controller.oldPanY + (-1 * controller.mousePressedY / controller.oldScaleXY) + (controller.mousePressedY / controller.scaleXY)
        elif mouseButton == LEFT:
            controller.panX = (mouseX - controller.mousePressedX) / controller.scaleXY + controller.oldPanX
            controller.panY = (mouseY - controller.mousePressedY) / controller.scaleXY + controller.oldPanY

    @transition('ReadyState')
    def mouseReleased(self, controller):
        controller.lastKeyCode = 0
        controller.changeState(ReadyState)

    def keyPressed(self, controller):
        controller.lastKeyCode = keyCode

    def keyReleased(self, controller):
        controller.lastKeyCode = 0


@singleton
class MenuWheel(State):

    def start(self, controller):
        controller.wheel = Wheel(mouseX, mouseY)

    def end(self, controller):
        controller.wheel = None

    @transition('NewTable')
    @transition('Save')
    @transition('Load')
    @transition('ReadyState')
    def mouseReleased(self, controller):
        menu_selection = controller.wheel.get_menu_selection()
        if menu_selection == "New":
            controller.changeState(NewTable)
        elif menu_selection == "Save":
            controller.changeState(Save)
        elif menu_selection == "Load":
            controller.changeState(Load)
        else:
            controller.changeState(ReadyState)


@singleton
class Load(State):

    def start(self, controller):
        selectInput("Input file", "fileSelected")

    @transition('ReadyState')
    def fileSelected(self, controller, selection):
        try:
            print selection, type(selection)
            if selection:
                new_tables = []
                selection_file_name = selection.getAbsolutePath()
                logging.debug(selection_file_name)
                controller.app_name = os.path.splitext(os.path.basename(selection_file_name))[0]
                with open(selection_file_name) as f:
                    d = yaml.load(f.read())
                    print d
                for model in d.get('models'):
                    table = Table(name=model.get('name'),
                                  x=model.get('x', random.randrange(int(controller.panX), int(width*controller.scaleXY + controller.panX))),
                                  y=model.get('y', random.randrange(int(controller.panY), int(height*controller.scaleXY + controller.panY))))
                    new_tables.append(table)
                    print "new table:", table
                    for field in model.get('fields'):
                        name = field.get('name')
                        ftype = field.get('type')
                        flen = field.get('len')
                        pk = field.get('pk', False)
                        column = Column(name=":".join(map(str, filter(None, [name, ftype, flen]))),
                                        x=model.get('x', 0),
                                        y=model.get('y', 0),
                                        pk=pk,
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
                            if len(ts) == 0:
                                new_table = Table(name=field.get('ref'),
                                                  x=random.randrange(int(controller.panX), int(width*controller.scaleXY + controller.panX)),
                                                  y=random.randrange(int(controller.panX), int(width*controller.scaleXY + controller.panX)),
                                                  external=True)
                                new_tables.append(new_table)
                                print "new external table:", table
                                ts = [new_table]
                            assert len(ts) == 1, repr(ts)
                            to_table = ts[0]
                            cs = [c for c in to_table.columns if c.name.partition(":")[0] == field.get('ref_field')]
                            if len(cs) == 0:
                                new_column = Column(name=field.get('ref_field'), x=0, y=0, pk=True, table=to_table)
                                to_table.columns.append(new_column)
                                cs = [new_column]
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
                                    print "When connecting {0}.{1} expected one table named {2} found {3}".format(from_table.name,
                                                                                                                  from_column.name,
                                                                                                                  field.get('ref'),
                                                                                                                  ts)
                            else:
                                print "When connecting {0}.{1} expected one column named {2} found {3}".format(from_table.name,
                                                                                                               field.get('name'),
                                                                                                               field.get('name'),
                                                                                                               cs)
                view_d = d.get('view', {})
                controller.modules = d.get('modules', [])
                controller.api = d.get('api', None)
                controller.panX = view_d.get('panX', 0)
                controller.panY = view_d.get('panY', 0)
                controller.scaleXY = view_d.get('scaleXY', 1)
                controller.tables = new_tables
            print "Read from {0}".format(selection)
            controller.changeState(ReadyState)
        except Exception:
            print traceback.format_exc()


@singleton
class Save(State):

    def start(self, controller):
        selectOutput("Output file", "fileSelected")

    @transition('ReadyState')
    def fileSelected(self, controller, selection):
        try:
            print selection, type(selection)
            if selection:
                app = {}
                app['app'] = os.path.splitext(os.path.basename(selection.getAbsolutePath()))[0]
                app['view'] = dict(panX=controller.panX, panY=controller.panY, scaleXY=controller.scaleXY)
                app['modules'] = controller.modules
                if controller.api:
                    app['api'] = controller.api
                controller.app_name = app['app']
                app['models'] = [t.to_dict() for t in controller.tables if not t.external]
                with open(selection.getAbsolutePath(), 'w') as f:
                    f.write(yaml.safe_dump(app, default_flow_style=False))
            print "Wrote to {0}".format(selection)
            controller.changeState(ReadyState)
        except Exception:
            print traceback.format_exc()


@singleton
class SelectedTable(State):

    def start(self, controller):
        if controller.selected_table:
            controller.selected_table.delete_empty_columns()
            controller.selected_table.add_empty_column()

    def end(self, controller):
        if controller.selected_table:
            controller.selected_table.delete_empty_columns()

    @transition('NameEdit')
    @transition('ColumnEdit')
    @transition('MouseSelect')
    def mousePressed(self, controller):
        table = controller.selected_table
        if not (controller.mousePX > table.left_extent and
                controller.mousePX < table.right_extent and
                controller.mousePY > table.top_extent and
                controller.mousePY < table.bottom_extent):
            self.end(controller)
            table.selected = False
            controller.selected_table = None
            controller.changeState(MouseSelect)
            return
        if (controller.mousePX > table.left_title_extent and
                controller.mousePX < table.right_title_extent and
                controller.mousePY > table.top_title_extent and
                controller.mousePY < table.bottom_title_extent):
            controller.changeState(NameEdit)
            return

        for column in table.columns:
            if (controller.mousePX > column.left_extent and
                    controller.mousePX < column.right_extent and
                    controller.mousePY > column.top_extent and
                    controller.mousePY < column.bottom_extent):
                controller.editing_column = column
                controller.changeState(ColumnEdit)
                return

    @transition('MoveTable')
    def mouseDragged(self, controller):
        controller.changeState(MoveTable)

    @transition('ReadyState')
    def keyTyped(self, controller):
        if key == DELETE or key == BACKSPACE:
            controller.selected_table.selected = False
            controller.tables.remove(controller.selected_table)
            controller.changeState(ReadyState)


@singleton
class NewTable(State):

    @transition('ReadyState')
    def start(self, controller):
        t = Table(name="New", x=controller.mousePX, y=controller.mousePY)
        controller.tables.append(t)
        controller.changeState(ReadyState)


@singleton
class MoveTable(State):

    def start(self, controller):
        controller.diffX = controller.mousePX - controller.selected_table.x
        controller.diffY = controller.mousePY - controller.selected_table.y

    def mouseDragged(self, controller):
        if controller.selected_table:
            controller.selected_table.x = controller.mousePX - controller.diffX
            controller.selected_table.y = controller.mousePY - controller.diffY

    @transition('SelectedTable')
    def mouseReleased(self, controller):
        controller.changeState(SelectedTable)


@singleton
class NameEdit(State):

    def start(self, controller):
        if controller.selected_table:
            controller.selected_table.edit = True

    def end(self, controller):
        if controller.selected_table:
            controller.selected_table.edit = False

    @transition('MouseSelect')
    def mousePressed(self, controller):
        table = controller.selected_table
        if not (controller.mousePX > table.left_title_extent and
                controller.mousePX < table.right_title_extent and
                controller.mousePY > table.top_title_extent and
                controller.mousePY < table.bottom_title_extent):
            controller.selected_table.edit = False
            controller.selected_table = None
            controller.changeState(MouseSelect)

    @transition('MoveTable')
    def mouseDragged(self, controller):
        controller.changeState(MoveTable)

    def keyReleased(self, controller):
        if keyCode == 8:
            controller.selected_table.name = controller.selected_table.name[:-1]

    @transition('SelectedTable')
    def keyTyped(self, controller):
        if key == CODED:
            if keyCode == 8:
                controller.selected_table.name = controller.selected_table.name[:-1]
        else:
            if key == RETURN:
                controller.changeState(SelectedTable)
            elif key == ENTER:
                controller.changeState(SelectedTable)
            elif key == BACKSPACE:
                controller.selected_table.name = controller.selected_table.name[:-1]
            elif key == DELETE:
                controller.selected_table.name = controller.selected_table.name[:-1]
            else:
                controller.selected_table.name += key


@singleton
class ColumnEdit(State):

    @transition('MouseSelect')
    def mousePressed(self, controller):
        column = controller.editing_column
        if not (controller.mousePX > column.left_extent and
                controller.mousePX < column.right_extent and
                controller.mousePY > column.top_extent and
                controller.mousePY < column.bottom_extent):
            self.end(controller)
            controller.selected_table = None
            controller.changeState(MouseSelect)

    def start(self, controller):
        controller.editing_column.edit = True

    def end(self, controller):
        if controller.editing_column:
            controller.editing_column.edit = False
            controller.editing_column = None
        if controller.selected_table:
            controller.selected_table.delete_empty_columns()

    def keyReleased(self, controller):
        if keyCode == 8:
            controller.editing_column.name = controller.editing_column.name[:-1]

    @transition('SelectedTable')
    def keyTyped(self, controller):
        if key == CODED:
            if keyCode == 8:
                controller.editing_column.name = controller.editing_column.name[:-1]
        else:
            if key == RETURN:
                controller.changeState(SelectedTable)
            elif key == ENTER:
                controller.changeState(SelectedTable)
            elif key == BACKSPACE:
                controller.editing_column.name = controller.editing_column.name[:-1]
            elif key == DELETE:
                controller.editing_column.name = controller.editing_column.name[:-1]
            else:
                controller.editing_column.name += key

    @transition('Connect')
    def mouseDragged(self, controller):
        controller.connecting_column = controller.editing_column
        controller.connecting_connector = ForeignKey(from_column=controller.connecting_column,
                                                     connecting=True)
        controller.connecting_column.connectors = [controller.connecting_connector]
        controller.changeState(Connect)


@singleton
class Connect(State):

    def end(self, controller):
        if (controller.connecting_connector and
                controller.connecting_connector.to_column is None):
            controller.connecting_column.connectors.remove(controller.connecting_connector)
        controller.connecting_connector = None
        controller.connecting_column = None

    @transition('ReadyState')
    def mouseReleased(self, controller):
        for table in controller.tables:
            for column in table.columns:
                if (controller.mousePX > column.left_extent and
                        controller.mousePX < column.right_extent and
                        controller.mousePY > column.top_extent and
                        controller.mousePY < column.bottom_extent):
                    controller.connecting_connector.to_column = column
                    break
        controller.changeState(ReadyState)
