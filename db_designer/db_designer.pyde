
page_height = 768
page_width = 1024

tables = []


class Table(object):
    
    def __init__(self, **kwargs):
        self.columns = []
        self.color = 255
        self.text_color = 0
        self.text_size = 48
        self.name = None
        self.x = None
        self.y = None
        self.width = 0
        self.height = 0
        self.__dict__.update(kwargs)
        
    def draw(self):
        
        fill(self.color)
        textSize(self.text_size)
        self.width = textWidth(self.name) + 20
        self.height = self.text_size + 30
        rect(self.x, self.y, self.width, self.height)
        fill(self.text_color)
        text(self.name, self.x + 10, self.y + self.text_size + 10)     
        
        previous_column = None
        for column in self.columns:
            column.draw(self, previous_column)
            previous_column = column
    
    
class Column(object):
    
    def __init__(self, **kwargs):
        self.name = None
        self.type = None
        self.len = None
        self.ref = None
        self.height = 100
        self.text_size = 24
        self.__dict__.update(kwargs)
        
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
    global tables

    size(page_width, page_height)
    t = Table(name="Gorilla", color="#804000", text_color=255, x=100, y=100)
    t.columns.append(Column(name="name"))
    t.columns.append(Column(name="is_alive"))
    tables.append(t)
    

def draw():
    for table in tables:
        table.draw() 
    
    
