# styles.py
class Styles:
    """统一管理所有组件样式的类"""
    
    @classmethod
    def box(cls):
        """基础Box组件样式"""
        return """
            border: none; 
            background-color: rgba(70, 70, 70, 0.4); 
            color: white;
        """
    
    @classmethod
    def slider(cls):
        """滑动条组件样式"""
        return """
            QSlider {
                background: rgba(70, 70, 70, 0.4);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::groove:horizontal {
                background: rgba(200, 200, 200, 0.2);
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """
    
    @classmethod
    def image_context_menu(cls):
        """图片上下文菜单样式"""
        return """
            QMenu {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                padding: 5px;
                border-radius: 7px;
            }
            QMenu::item {
                color: #DCDCDC;
                padding: 5px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
            }
        """

    @classmethod
    def image_box_hover(cls):
        """图片框悬停样式"""
        return """
            QLabel:hover {
                border: 1px solid #3F3F46;
                background-color: rgba(70, 70, 70, 0.6);
            }
        """

    @classmethod
    def general_menu(cls):
        """通用菜单样式"""
        return """
            QMenu {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                padding: 5px;
                border-radius: 7px;
            }
            QMenu::item {
                color: #DCDCDC;
                padding-left: 7px;
                padding-right: 15px;
                padding-top: 8px;
                padding-bottom: 8px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #3E3E40;
            }
            QMenu::item:disabled {
                color: #808080;
            }
            QMenu::separator {
                height: 1px;
                background: #3F3F46;
                margin: 5px 0;
            }
        """
    
    @classmethod
    def image_label_placeholder(cls):
        """图片标签占位符样式"""
        return """
            border: none; 
            background-color: rgba(70, 70, 70, 0.4); 
            color: white;
            qproperty-alignment: AlignCenter;
        """
