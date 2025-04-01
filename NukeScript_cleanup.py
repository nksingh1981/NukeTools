import nuke
from PySide6 import QtWidgets


""" This script will remove all the unused , disabled and unwanted nodes from the script."""
class NodeCleanupUI(QtWidgets.QWidget):
    def __init__(self):
        super(NodeCleanupUI, self).__init__()
        self.setWindowTitle("NukeScript Cleanup Tool")
        self.setFixedSize(300, 150)

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Checkboxes
        self.cb_remove_disabled = QtWidgets.QCheckBox("Remove Disabled Nodes")
        self.cb_remove_blur = QtWidgets.QCheckBox("Remove Unwanted Nodes")

        # Buttons
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        # Add widgets to layout
        layout.addWidget(self.cb_remove_disabled)
        layout.addWidget(self.cb_remove_blur)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        # Connect signals
        self.ok_button.clicked.connect(self.run_cleanup)
        self.cancel_button.clicked.connect(self.close)

    def run_cleanup(self):
        """Runs the selected cleanup functions."""
        if self.cb_remove_disabled.isChecked():
            remove_disabled_nodes()
        if self.cb_remove_blur.isChecked():
            remove_unwanted_nodes()
        self.close()

def remove_disabled_nodes():
    """Delete all disabled nodes from the script."""
    for node in nuke.allNodes():
        if node.knob('disable') and node['disable'].value():
            print("Deleted disabled node: {}".format(node.name()))
            nuke.delete(node)

def remove_unwanted_nodes():
    """ Removes all the unwanted nodes from the nuke script """
    if nuke.ask("This will delete all the unused and unwanted node in script"):
        dependencies = []
        nodes_to_process = nuke.allNodes("Write" or "DeepWrite")
        while nodes_to_process:
            node = nodes_to_process.pop(0)
            if node not in dependencies:
                dependencies.append(node)
                nodes_to_process.extend(node.dependencies())
        for n in [d for d in nuke.allNodes() if d not in dependencies]:
            nuke.delete(n)
    else:
        pass

def launch_cleanup_ui():
    """Launch the Nuke Cleanup UI."""
    global cleanup_window
    cleanup_window = NodeCleanupUI()
    cleanup_window.show()

