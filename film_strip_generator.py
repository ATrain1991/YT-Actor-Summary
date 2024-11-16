from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt6.QtCore import QSize, Qt
from typing import Type

class FilmStripWidget(QWidget):
    def __init_from_widgets__(self, frames: list[QWidget], width=1080, height=1920):
        """
        Create a vertical filmstrip from a list of existing widgets
        
        Args:
            frames: List of QWidget instances to use as frames
            width: Width of each frame in pixels
            height: Height of each frame in pixels
        """
        super().__init__()
        self.frame_width = width
        self.frame_height = height
        self.num_frames = len(frames)

        # Create scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedWidth(self.frame_width)
        scroll.setFixedHeight(self.frame_height)

        # Create container widget for frames
        container = QWidget()
        
        # Create vertical layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add provided frames
        self.frames = []
        for i, frame in enumerate(frames):
            frame.setFixedSize(QSize(self.frame_width, self.frame_height))
            layout.addWidget(frame)
            # Add separator between frames except for last one
            # if i < len(frames) - 1:
                # separator = QWidget()
                # separator.setFixedSize(QSize(self.frame_width, 2))  # 2 pixel high line
                # separator.setStyleSheet("background-color: black;")
                # layout.addWidget(separator)
            # self.frames.append(frame)
            
        container.setLayout(layout)
        scroll.setWidget(container)

        # Add scroll area to main layout
    def __init__(self, frame_widget_class: Type[QWidget] = QWidget, width=1080, height=1920, frames=6, **widget_kwargs):
        """
        Create a vertical filmstrip of custom widgets
        
        Args:
            frame_widget_class: The widget class to use for each frame
            width: Width of each frame in pixels
            height: Height of each frame in pixels 
            frames: Number of frames in the strip
            widget_kwargs: Additional keyword arguments passed to frame widget constructor
        """
        super().__init__()
        self.frame_width = width
        self.frame_height = height
        self.num_frames = frames

        # Create scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedWidth(self.frame_width)
        scroll.setFixedHeight(self.frame_height)

        # Create container widget for frames
        container = QWidget()
        
        # Create vertical layout
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create frames using provided widget class
        self.frames = []
        for _ in range(self.num_frames):
            frame = frame_widget_class(**widget_kwargs)
            frame.setFixedSize(QSize(self.frame_width, self.frame_height))
            layout.addWidget(frame)
            # Add black separator line between frames
            if _ < self.num_frames - 1:  # Don't add line after last frame
                separator = QWidget()
                separator.setFixedSize(QSize(self.frame_width, 2))  # 2 pixel high line
                separator.setStyleSheet("background-color: black;")
                layout.addWidget(separator)
            self.frames.append(frame)
            
        container.setLayout(layout)
        scroll.setWidget(container)

        # Add scroll area to main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def get_frame(self, index):
        """Get a specific frame widget by index"""
        if 0 <= index < self.num_frames:
            return self.frames[index]
        return None
    
    def get_all_frames(self):
        """Get list of all frame widgets"""
        return self.frames

    def update_frames(self, new_frames: list[QWidget]):
        """Update the filmstrip with new frame widgets"""
        # Find the container widget (the one inside the scroll area)
        scroll_area = self.findChild(QScrollArea)
        container = scroll_area.widget()
        layout = container.layout()
        
        # Clear existing frames
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add new frames
        for i, frame in enumerate(new_frames):
            frame.setFixedSize(QSize(self.frame_width, self.frame_height))
            layout.addWidget(frame)
            # Add black separator line between frames
            if i < len(new_frames) - 1:  # Don't add line after last frame
                separator = QWidget()
                separator.setFixedSize(QSize(self.frame_width, 2))
                separator.setStyleSheet("background-color: black;")
                layout.addWidget(separator)
            self.frames.append(frame)
        
        self.num_frames = len(new_frames)

