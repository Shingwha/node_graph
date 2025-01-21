# theme.py
class Color:
    """颜色配置"""
    # 基础颜色
    BACKGROUND = "#212121"
    GRID = "#313131"
    CHUNK = "#151515"
    
    # 节点颜色
    NODE_DEFAULT = "#50B780"
    NODE_SELECTED = "#F2E383"
    NODE_TITLE = "#1F7D6B"
    NODE_TITLE_FONT = "#FFFFFF"
    IMAGE_NODE = "#c36060"
    
    # 组件颜色
    BOX_BACKGROUND = "rgba(70, 70, 70, 0.4)"
    TEXT_WHITE = "white"
    SLIDER_HANDLE = "white"
    SLIDER_GROOVE = "rgba(200, 200, 200, 0.2)"
    
    # 菜单颜色
    MENU_BG = "#2D2D30"
    MENU_BORDER = "#3F3F46"
    MENU_ITEM_HOVER = "#3E3E40"
    MENU_TEXT = "#DCDCDC"
    MENU_DISABLED_TEXT = "#808080"

class Font:
    """字体配置"""
    NODE_TITLE = "Helvetica"
    NODE_TITLE_SIZE = 8

class Dimensions:
    """尺寸配置"""
    # 节点尺寸
    NODE_WIDTH = 120
    NODE_TITLE_HEIGHT = 20
    NODE_EDGE_RADIUS = 3
    NODE_PADDING = 5
    NODE_SPACING = 7
    NODE_OPACITY = 0.7
    
    # 组件尺寸
    SLIDER_HEIGHT = "4px"
    SLIDER_HANDLE_SIZE = "12px"
    BOX_HEIGHT = 20
    
    # 网格尺寸
    GRID_SIZE = 30
    GRID_CHUNK = 5

class StyleSheets:
    """样式表配置"""
    @staticmethod
    def box():
        return f"""
            border: none; 
            background-color: {Color.BOX_BACKGROUND}; 
            color: {Color.TEXT_WHITE};
        """
    
    @staticmethod
    def slider():
        return f"""
            QSlider {{
                background: {Color.BOX_BACKGROUND};
                height: {Dimensions.SLIDER_HEIGHT};
                border-radius: 2px;
            }}
            QSlider::groove:horizontal {{
                background: {Color.SLIDER_GROOVE};
                height: {Dimensions.SLIDER_HEIGHT};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {Color.SLIDER_HANDLE};
                width: {Dimensions.SLIDER_HANDLE_SIZE};
                height: {Dimensions.SLIDER_HANDLE_SIZE};
                margin: -4px 0;
                border-radius: 6px;
            }}
        """
    
    @staticmethod
    def general_menu():
        return f"""
            QMenu {{
                background-color: {Color.MENU_BG};
                border: 1px solid {Color.MENU_BORDER};
                padding: 5px;
                border-radius: 7px;
            }}
            QMenu::item {{
                color: {Color.MENU_TEXT};
                padding-left: 7px;
                padding-right: 15px;
                padding-top: 8px;
                padding-bottom: 8px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {Color.MENU_ITEM_HOVER};
            }}
            QMenu::item:disabled {{
                color: {Color.MENU_DISABLED_TEXT};
                opacity: 0.5;
            }}
            QMenu::separator {{
                height: 1px;
                background: {Color.MENU_BORDER};
                margin: 5px 0;
            }}
        """
    

    
    @staticmethod
    def image_label_placeholder():
        return StyleSheets.box()
