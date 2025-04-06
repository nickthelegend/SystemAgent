from src.agent.system.tree.views import TreeElementNode,BoundingBox,CenterCord,TreeState
from uiautomation import GetRootControl,Control,ControlFromPoint
from src.agent.system.tree.config import INTERACTIVE_CONTROL_TYPE_NAMES
from PIL import Image,ImageDraw,ImageFont
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from src.agent.system.desktop import Desktop

class Tree:
    def __init__(self,desktop:'Desktop'):
        self.desktop=desktop

    def get_state(self,use_vision:bool=False)->tuple[bytes,TreeState]:
        root=GetRootControl()
        nodes=self.get_interactive_nodes(node=root)
        if use_vision:
            annotate=self.annotate(nodes=nodes,save_screenshot=False)
            screenshot=self.desktop.screenshot_in_bytes(screenshot=annotate)
        else:
            screenshot=None
        selector_map=self.build_selector_map(nodes=nodes)
        return (screenshot,TreeState(nodes=nodes,selector_map=selector_map))

    def get_interactive_nodes(self, node: Control) -> list[TreeElementNode]:
        interactive_nodes = []
        def is_window_minimized(node: Control):
            return node.ControlTypeName in ['WindowControl','PaneControl']  and node.IsMinimize()

        def is_element_interactive(node: Control):
            if node.ControlTypeName in INTERACTIVE_CONTROL_TYPE_NAMES:
                if is_element_visible(node):
                    if node.IsEnabled:
                        return True
            return False
        
        def is_element_visible(node:Control,threshold:int=0):
            box=node.BoundingRectangle
            width=box.width()
            height=box.height()
            area=width*height
            is_offscreen=not node.IsOffscreen
            return area > threshold and is_offscreen
            
        def tree_traversal(node: Control):
            if is_element_interactive(node) and not is_window_minimized(node):
                box = node.BoundingRectangle
                bounding_box = BoundingBox(
                    left=box.left,
                    top=box.top,
                    right=box.right,
                    bottom=box.bottom
                )
                center = CenterCord(x=box.xcenter(), y=box.ycenter())
                interactive_nodes.append(TreeElementNode(
                    name=node.Name.strip(),
                    control_type=node.ControlTypeName,
                    shortcut=node.AcceleratorKey,
                    bounding_box=bounding_box,
                    center=center,
                    handle=node
                ))
            # Recursively check all children
            for child in node.GetChildren():
                tree_traversal(child)

        tree_traversal(node)
        return interactive_nodes

    def get_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def annotate(self,nodes:list[TreeElementNode],save_screenshot:bool=False)->Image:
        screenshot=self.desktop.get_screenshot()
        # Include padding to the screenshot
        padding=20
        width=screenshot.width+(2*padding)
        height=screenshot.height+(2*padding)
        padded_screenshot=Image.new("RGB", (width, height), color=(255, 255, 255))
        padded_screenshot.paste(screenshot, (padding,padding))
        # Create a layout above the screenshot to place bounding boxes.
        draw=ImageDraw.Draw(padded_screenshot)
        font_size=12
        try:
            font=ImageFont.truetype('arial.ttf',font_size)
        except:
            font=ImageFont.load_default()
        for label,node in enumerate(nodes):
            box=node.bounding_box
            color=self.get_random_color()
            # Adjust bounding box to fit padded image
            adjusted_box = (
                box.left + padding, box.top + padding,  # Adjust top-left corner
                box.right + padding, box.bottom + padding  # Adjust bottom-right corner
            )
            # Draw bounding box around the element in the screenshot
            draw.rectangle(adjusted_box,outline=color,width=2)
            
            # Get the size of the label
            label_width=draw.textlength(str(label),font=font,font_size=font_size)
            label_height=font_size
            left,top,right,bottom=adjusted_box
            # Position the label above the bounding box and towards the right
            label_x1 = right - label_width  # Align the right side of the label with the right edge of the box
            label_y1 = top - label_height - 4  # Place the label just above the top of the bounding box, with some padding

            # Draw the label background rectangle
            label_x2 = label_x1 + label_width
            label_y2 = label_y1 + label_height + 4  # Add some padding

            # Draw the label background rectangle
            draw.rectangle([(label_x1, label_y1), (label_x2, label_y2)], fill=color)

            # Draw the label text
            text_x = label_x1 + 2  # Padding for text inside the rectangle
            text_y = label_y1 + 2
            draw.text((text_x, text_y), str(label), fill=(255, 255, 255), font=font)

        if save_screenshot:
            self.desktop.save_screenshot(padded_screenshot)
        return padded_screenshot
    
    def get_annotated_image_data(self,save_screenshot=False)->tuple[Image,list[TreeElementNode]]:
        root=GetRootControl()
        nodes=self.get_interactive_nodes(node=root)
        screenshot=self.annotate(nodes=nodes,save_screenshot=save_screenshot)
        return screenshot,nodes

    def build_selector_map(self, nodes: list[TreeElementNode]) -> dict[int, TreeElementNode]:
        return {index:node for index,node in enumerate(nodes)}