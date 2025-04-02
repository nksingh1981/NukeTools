# Align the nodes in the node graph with respect to write node.
import nuke


def align_nodes():
    write_nodes = [node for node in nuke.allNodes() if node.Class() == "Write"]

    for write_node in write_nodes:
        process_dependencies(write_node, write_node.xpos(), write_node.ypos(), {}, set())


def process_dependencies(node, x_pos, y_pos, occupied_positions, visited_nodes):
    if node in visited_nodes:
        return
    visited_nodes.add(node)

    y_offset = 200  # Vertical spacing
    x_offset = 200  # Horizontal spacing

    dependencies = node.dependencies(nuke.INPUTS)  # Get upstream nodes
        # Align according to its input() to the same X position and Y position as the dependent node
    for i, dep_node in enumerate(dependencies):
        if i == 0:

            new_x, new_y = x_pos, y_pos - y_offset
        elif i == 1:

            new_x, new_y = x_pos - x_offset, y_pos
        else:
            # Stagger additional dependencies to prevent overlap
            new_x, new_y = x_pos - (i * x_offset), y_pos - ((i + 1) * y_offset)

        # Check if the position is already occupied, if so, shift the nodes
        while (new_x, new_y) in occupied_positions:
            new_y -= y_offset  # Move down to avoid overlap

        # Store occupied positions to avoid overlaps
        occupied_positions[(new_x, new_y)] = dep_node

        dep_node.setXpos(new_x)
        dep_node.setYpos(new_y)

        process_dependencies(dep_node, new_x, new_y, occupied_positions, visited_nodes)


align_nodes()