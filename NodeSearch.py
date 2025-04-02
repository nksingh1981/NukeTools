import re as _re
import nuke as _nuke
from PySide6 import QtWidgets as _QtWidgets
from PySide6 import QtCore as _QtCore
from PySide6.QtGui import QTextCursor, QCursor


class SearchListWidget(_QtWidgets.QDialog):
    """ Creates a list widgets with items populated from the initializer input list

        List widgets contains the node list as its items. The list has functionality to focus on any node clicket in the item list

        Extends:
           _QtWidgets.QDialog

        Variables:
            searchResult[list]: Holds the list for which list widget is to be created
            nodes[nuke.nodes]: All the nodes contained in the composition

    """
    def __init__(self, searchResult = None, nodes = None, on_create = None, parent = None, winflags = None):
        super(SearchListWidget, self).__init__(parent = parent)
        if winflags is not None:
            self.setWindowFlags(winflags)

        self._nodes = nodes
        self._searchResult = searchResult

        self.setMinimumSize(200, 300)
        self.setMaximumSize(600, 700)

        #The main layout for UI
        self.mainLayout = _QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)

        # Find nodes with the Search term
        self._searchList = _QtWidgets.QListWidget()
        self._searchList.itemActivated.connect(self._item_click)
        self._searchList.itemClicked.connect(self._item_click)

        self.mainLayout.addWidget(self._searchList)
        self.setLayout(self.mainLayout)

        if self._searchResult:
            for node in self._searchResult:
                item = _QtWidgets.QListWidgetItem(node.fullName())
                self._searchList.addItem(item)

    def _item_click(self, item):
        nodeFullName = str(item.text())
        # Deselect all the nodes
        for node in self._nodes:
            node["selected"].setValue(False)

        for node in self._searchResult:
            if node.fullName() == nodeFullName:
                node["selected"].setValue(True)
                # Select and zoom on the node
                if "." in nodeFullName:
                    s = nodeFullName.split(".")
                    lastIndex = len(s)-1
                    del s[lastIndex]
                    # Parent group name constituted
                    rebuiltName = ".".join(s)
                    for i in self._nodes:
                        if i.fullName() == rebuiltName:
                            i.begin()
                            _nuke.showDag(i)
                            _nuke.show(node)
                            _nuke.zoom(1, [node.xpos(), node.ypos()])
                            i.end()
                else:
                    _nuke.showDag(_nuke.root())
                    _nuke.show(node)
                    _nuke.zoom(1, [node.xpos(), node.ypos()])
        return True

    def event(self, event):
        if event.type() == _QtCore.QEvent.WindowDeactivate:
            return True
        else:
            return super(SearchListWidget,self).event(event)

    def show(self):
        super(SearchListWidget, self).show()

    def centerToscreen(self):
        # get cursor position, and screen dimension on active screen
        cursor = QCursor().pos()
        screen = _QtWidgets.QApplication.screenAt(cursor).geometry()

        # Set the UI position to the center of the screen
        xpos = (screen.right() - screen.left() - self.width() /2) /2
        ypos = (screen.bottom() - screen.top() - self.height() /2) /2

        # Move Window
        self.move(xpos, ypos)

    def close(self ):
        super(SearchListWidget, self).close()


class RecursiveNodeSearchWidget(_QtWidgets.QDialog):
    """ Creates a widget to get user input for node search

    The user input string or regular expression is used to find nodes matchng the criteria
    anywhere in the nuke script

    Extends:
        _QtWidgets.QDialog

    Variables:
        _inputMessage[string]: TextEdit widget for holding UI info message
        _inputMsgFont[QTextEdit.font]: Fot for UI info message
        _userInputFont[QTextEdit.font]: Font for user input edit lin
        _textmsg[string]: UI info message string
        _buttonGroupBox[QtWidgets.QGroupBox]: Qt horizontal layout
        _hLayout[QtWidgets.QHBoxLayout]: Qt horizontal layout
        _okButton[QtWidgets.QPushButton]: Qt button handle for submit
        _cancleButton[QtWidgets.QPushButton]: Qt button handle for operation cancle
        _userInput[QtWidgets.QLineEdit]: widget to take user's input
        _nodeListWidget[SearchListWidget]: object of SearchListWidget class for search result display
        """
    def __init__(self, on_create = None, parent = None, winflags = None):
        super(RecursiveNodeSearchWidget,self).__init__(parent = parent)
        if winflags is not None:
            for flag in winflags:
                self.setWindowFlags(flag)

        self.setMinimumSize(240, 130)
        self.setMaximumSize(240, 130)
        self.setToolTip("Pattern search for nodes. Backdrop and stickynotes can be\nsearched using labels also.\nPython regular expression are fully supported.")

        # The main layout for UI
        self.mainLayout = _QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        #Message test
        self._inputMessage = _QtWidgets.QTextEdit(parent)
        self._inputMessage.setReadOnly(True)
        self._inputMessage.moveCursor(QTextCursor.End)
        self._inputMsgFont = self._inputMessage.font()
        self._inputMsgFont.setFamily("Courier")
        self._inputMsgFont.setPointSize(10)
        self._inputMessage.setCurrentFont(self._inputMsgFont)
        self._textMsg = "Select all nodes containing:\n(or Regular Expression)"
        self._inputMessage.insertPlainText(self._textMsg)
        self._inputMessage.setMinimumSize(240, 50)
        self._inputMessage.setMaximumSize(240, 50)
        self._inputMessage.setStyleSheet("border:0;")
        self.mainLayout.addWidget(self._inputMessage)

        # Layout for buttons
        self._buttonGroupBox = _QtWidgets.QGroupBox()
        self._buttonGroupBox.setFlat(True)
        self._hLayout = _QtWidgets.QHBoxLayout()
        self._hLayout.setContentsMargins(0, 0, 0, 0)
        self._buttonGroupBox.setLayout(self._hLayout)

        # ok button
        self._okButton = _QtWidgets.QPushButton('OK')
        self._okButton.setMinimumSize(60, 30)
        self._okButton.setMaximumSize(60, 30)
        self._okButton.clicked.connect(self._okButtonHandle)

        # Cancel button
        self._cancelButton = _QtWidgets.QPushButton('Cancel')
        self._cancelButton.setMinimumSize(60, 30)
        self._cancelButton.setMaximumSize(60, 30)
        self._cancelButton.clicked.connect(self._cancelButtonHandle)

        #Add buttons to the layout
        self._hLayout.addWidget(self._okButton)
        self._hLayout.addWidget(self._cancelButton)

        # Add button group to the layout
        self.mainLayout.addWidget(self._buttonGroupBox)
        self._userInput = _QtWidgets.QLineEdit()
        self._userInput.setPlaceholderText("Search text.....")
        self._userInput.setMinimumSize(240, 40)
        self._userInput.setMaximumSize(240, 40)
        self._userInput.setContentsMargins(5, 5, 5, 5)
        self._userInputFont = self._userInput.font()
        self._userInputFont.setPointSize(10)
        self._userInput.setFont(self._userInputFont)
        self.mainLayout.addWidget(self._userInput)
        self.setLayout(self.mainLayout)

    def _okButtonHandle(self):

        if not str(self._userInput.text()):
            _nuke.message("Please enter a search term")
            self.activateWindow()
            self.raise_()
            self._userInput.setFocus()
            return True
        # find nodes with the search term
        nodesFound = self._findNodes(str(self._userInput.text()))
        if nodesFound:
            self._nodeListWidget = SearchListWidget(searchResult=nodesFound, nodes=self._nodes, winflags=_QtCore.Qt.Tool)
            self._nodeListWidget.centerToscreen()
            self._nodeListWidget.show()
            self._nodeListWidget.raise_()
            self.close()
        else:
            _nuke.message('Nothing Found!')
            self.activateWindow()
            self.raise_()
            self._userInput.setFocus()
            return True

    def _cancelButtonHandle(self):
        self.close()
        return True

    def event(self, event):
        if event.type() == _QtCore.QEvent.WindowDeactivate:
            return True
        else:
            return super(RecursiveNodeSearchWidget, self).event(event)

    def show(self):
        self._userInput.setFocus()
        super(RecursiveNodeSearchWidget, self).show()

    def centerToscreen(self):
        # get cursor position and screen dimension on active screen
        cursor = QCursor().pos()
        screen = _QtWidgets.QApplication.screenAt(cursor).geometry()

        # Set the UI position to the center of the screen
        xpos = (screen.right() - screen.left() - self.width()) / 2
        ypos = (screen.bottom() - screen.top() - self.height()) /2

        # move window
        self.move(xpos, ypos)

    def close(self):
        super(RecursiveNodeSearchWidget, self).close()

    def _findNodes(self, userInput):
        """ This function tires to find all the nodes whose names match the input pattern.

        Regular expression are also supported. Backdrop and sticky notes are searched for their names as well as their labels.

        Args:
            userInput ([string]): The user input search test

        Returns:
            nodeList[list]: List of nodes found as result of pattern search
        """
        self._nodes = _nuke.allNodes(recurseGroups=True)
        nodeList = []
        controlCharList = ['+', '?', '.', '*', '^', '$', '(', ')', '[', ']', '{', '}', '|', '\'']
        if not any (s in userInput for s in controlCharList):
            userInput = "^" + userInput
        for n in self._nodes:
            if n.Class() == "StickyNote" or n.Class() == "BackdropNode":
                if _re.search(userInput, str(n["label"].getValue()), _re.I):
                    if self._isAnyParentGizmo(n):
                        continue
                    nodeList.append(n)
                    continue
            if _re.search(userInput, n.name(), _re.I):
                if self._isAnyParentGizmo(n):
                    continue
                nodeList.append(n)
        return nodeList

    def _isAnyParentGizmo(self, node):
        """ Tries to find wheather the found node is inside a gizmo/excluded group nodes or not

        Args:
            node ([nuke node]): The node for which the query is executed

        Returns:
            bool: True if any parent node in its heirarchy is a gizmo/excluded group node
        """
        excludeList = ["Noop"]
        nodeFullName = node.fullName()
        if '.' in nodeFullName:
            splitList = nodeFullName.split('.')
            currentFullName = splitList[0]
            for count in range(len(splitList) - 1):
                for exclNode in excludeList:
                    if exclNode in currentFullName:
                        return True
                if currentFullName == nodeFullName:
                    break
                for node in self._nodes:
                    if node.fullName() == currentFullName:
                        if isinstance(node, _nuke.Gizmo):
                            return True
                currentFullName = currentFullName + '.' + splitList[count + 1]
        return False


def main():
    global inputWidget
    inputWidget = RecursiveNodeSearchWidget(winflags=[_QtCore.Qt.Tool, _QtCore.Qt.WindowStaysOnTopHint])
    inputWidget.centerToscreen()
    inputWidget.show()
    inputWidget.raise_()
    inputWidget.activateWindow()
