from PyQt5.QtWidgets import QApplication, QComboBox, QStyledItemDelegate, QStyle, QMessageBox, QWidget, QVBoxLayout, QListView, QPushButton
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPainter


class Item:
    def __init__(self, name):
        self.name = name

    def delete(self):
        print(f"Item '{self.name}' is deleted!")
        items.remove(self)


items = [Item("Item 1"), Item("Item 2"), Item("Item 3")]


class RemoveItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(RemoveItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        
        # Only paint the close icon if there are more than one items in the combobox
        if self.parent().count() > 1:
            close_icon =  self.parent().style().standardIcon(QStyle.SP_DockWidgetCloseButton)
            rect = self.get_close_button_rect(option.rect)
            close_icon.paint(painter, rect)

    def get_close_button_rect(self, item_rect):
        icon_size = 16
        return QRect(item_rect.right() - icon_size - 5, item_rect.center().y() - icon_size // 2, icon_size, icon_size)


class CustomListView(QListView):
    def __init__(self, combo, parent=None):
        super(CustomListView, self).__init__(parent)
        self._combo = combo

    def mousePressEvent(self, event):
        combo = self._combo
        delegate = combo.itemDelegate()
        index_under_mouse = self.indexAt(event.pos())

        if combo.count() <= 1:  # If only one item left, don't process any further
            super().mousePressEvent(event)
            return

        if isinstance(delegate, RemoveItemDelegate) and delegate.get_close_button_rect(self.visualRect(index_under_mouse)).contains(event.pos()):
            reply = QMessageBox.question(self, "Confirmation", "Are you sure you want to remove this item?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                item_to_remove = items[index_under_mouse.row()]
                item_to_remove.delete()
                combo.removeItem(index_under_mouse.row())
        else:
            super().mousePressEvent(event)

class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CustomComboBox, self).__init__(parent)
        self.setView(CustomListView(self))
        self.setItemDelegate(RemoveItemDelegate(self))

    def addNewItem(self, item):
        self.addItem(item.name)
        items.append(item)

app = QApplication([])

window = QWidget()
layout = QVBoxLayout(window)

combo = CustomComboBox(window)
for item in items:
    combo.addItem(item.name)

layout.addWidget(combo)

# Button to add a new item
add_button = QPushButton("Add Item", window)
add_button.clicked.connect(lambda: combo.addNewItem(Item(f"Item {len(items) + 1}")))
layout.addWidget(add_button)

window.setLayout(layout)
window.resize(400, 300)
window.show()

app.exec_()

