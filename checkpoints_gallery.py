import sys
import json
import os
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QScrollArea, QTabWidget, QSlider, QLineEdit, QTextEdit,
                             QGridLayout, QFrame, QDialog, QComboBox, QLayout, QSizePolicy,
                             QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QDrag, QPalette, QPen

# Import config and styles from new location
from config.settings import config

# Import custom widgets
from widgets import CardDetailsDialog

CRITERIA_LIST = ["beauty", "noErrors", "loras", "Pos prompt", "Neg prompt"]

# Get styles dynamically
def get_styles():
    """Get current styles module"""
    return config.get_styles()


class OptionsDialog(QDialog):
    """Dialog for application options"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(config.get_text('options_title'))
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Language selection
        lang_group = QGroupBox(config.get_text('options_language'))
        lang_layout = QHBoxLayout()
        
        self.lang_fr = QCheckBox("Français")
        self.lang_en = QCheckBox("English")
        
        # Set current language
        current_lang = config.get('language')
        if current_lang == 'fr':
            self.lang_fr.setChecked(True)
        else:
            self.lang_en.setChecked(True)
        
        # Make them mutually exclusive
        self.lang_fr.toggled.connect(lambda checked: self.lang_en.setChecked(not checked) if checked else None)
        self.lang_en.toggled.connect(lambda checked: self.lang_fr.setChecked(not checked) if checked else None)
        
        lang_layout.addWidget(self.lang_fr)
        lang_layout.addWidget(self.lang_en)
        lang_layout.addStretch()
        lang_group.setLayout(lang_layout)
        
        # Theme selection
        theme_group = QGroupBox(config.get_text('options_theme'))
        theme_layout = QHBoxLayout()
        
        self.theme_dark = QCheckBox(config.get_text('options_theme_dark'))
        self.theme_light = QCheckBox(config.get_text('options_theme_light'))
        
        # Set current theme
        try:
            current_theme = config.get('theme')
        except:
            current_theme = 'dark'

        if current_theme == 'dark':
            self.theme_dark.setChecked(True)
        else:
            self.theme_light.setChecked(True)

        # Make them mutually exclusive
        self.theme_dark.toggled.connect(lambda checked: self.theme_light.setChecked(not checked) if checked else None)
        self.theme_light.toggled.connect(lambda checked: self.theme_dark.setChecked(not checked) if checked else None)
        
        theme_layout.addWidget(self.theme_dark)
        theme_layout.addWidget(self.theme_light)
        theme_layout.addStretch()
        theme_group.setLayout(theme_layout)
        
        # Import mode
        import_group = QGroupBox(config.get_text('options_import_mode'))
        import_layout = QHBoxLayout()
        
        self.import_replace = QCheckBox(config.get_text('options_import_replace'))
        self.import_add = QCheckBox(config.get_text('options_import_add'))
        
        current_mode = config.get('import_mode')
        if current_mode == 'add':
            self.import_add.setChecked(True)
        else:
            self.import_replace.setChecked(True)
        
        # Make them mutually exclusive
        self.import_replace.toggled.connect(lambda checked: self.import_add.setChecked(not checked) if checked else None)
        self.import_add.toggled.connect(lambda checked: self.import_replace.setChecked(not checked) if checked else None)
        
        import_layout.addWidget(self.import_add)
        import_layout.addWidget(self.import_replace)
        import_layout.addStretch()
        import_group.setLayout(import_layout)
        
        # Close button
        close_btn = QPushButton(config.get_text('options_close'))
        close_btn.clicked.connect(self.save_and_close)
        
        layout.addWidget(lang_group)
        layout.addWidget(theme_group)
        layout.addWidget(import_group)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def save_and_close(self):
        # Save language
        if self.lang_fr.isChecked():
            config.set_language('fr')
        else:
            config.set_language('en')
        # Save theme
        if self.theme_dark.isChecked():
            config.set_theme('dark')
        else:
            config.set_theme('light')
        # Save import mode
        if self.import_replace.isChecked():
            config.set_import_mode('replace')
        else:
            config.set_import_mode('add')
        
        # Notify parent to refresh UI
        if isinstance(self.parent(), MainWindow):
            self.parent().refresh_ui_texts()
            self.parent().apply_styles()  # Apply new theme styles
        
        self.accept()


class FlowLayout(QLayout):
    """Layout that arranges widgets in a flow like HTML divs"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self.item_list:
            widget = item.widget()
            space_x = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal
            )
            space_y = spacing + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical
            )
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()


class ImageCard(QFrame):
    positionChanged = pyqtSignal()
    
    def __init__(self, image_path, checkpoint_name, parent=None, source_json=None):
        super().__init__(parent)
        self.image_path = image_path
        self.checkpoint_name = checkpoint_name
        self.source_json = source_json  # Track which JSON file this card came from
        self.criteria = {c: 0 for c in CRITERIA_LIST}
        self.total_score = 0
        
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setAcceptDrops(True)
        self.drag_start_pos = None
        self.press_timer = QTimer()
        self.press_timer.setSingleShot(True)
        self.press_timer.timeout.connect(self.start_drag_operation)
        self.long_press_started = False
        
        # Dark mode style
        self.setStyleSheet(get_styles().card_style())
        
        # Prevent card from stretching
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # Details popup
        self.details_popup = None
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)
        
        # Top bar
        top_layout = QHBoxLayout()
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.setStyleSheet(get_styles().close_button())
        self.close_btn.clicked.connect(self.delete_card)
        
        self.checkpoint_label = QLabel(self.checkpoint_name)
        self.checkpoint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.checkpoint_label.setStyleSheet(get_styles().checkpoint_label())
        
        self.score_label = QLabel("0")
        self.score_label.setFixedSize(40, 40)
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_score_display()
        
        top_layout.addWidget(self.close_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.checkpoint_label)
        top_layout.addStretch()
        top_layout.addWidget(self.score_label)
        
        # Image container for centering
        image_container = QWidget()
        image_container_layout = QHBoxLayout()
        image_container_layout.setContentsMargins(0, 0, 0, 0)
        image_container_layout.addStretch()
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        
        image_container_layout.addWidget(self.image_label)
        image_container_layout.addStretch()
        image_container.setLayout(image_container_layout)
        
        self.load_image(210)
        
        # Criteria buttons with FlowLayout for dynamic wrapping
        criteria_widget = QWidget()
        criteria_flow = FlowLayout(criteria_widget, margin=0, spacing=5)
        
        self.criteria_buttons = {}
        
        # Calculate button size based on longest text with proper padding
        temp_btn = QPushButton()
        font_metrics = temp_btn.fontMetrics()
        max_width = 0
        for criterion in CRITERIA_LIST:
            text_width = font_metrics.horizontalAdvance(criterion)
            max_width = max(max_width, text_width)
        
        button_width = max_width + 20
        
        for criterion in CRITERIA_LIST:
            btn = QPushButton(criterion)
            btn.setFixedSize(button_width, 30)
            btn.setCheckable(False)
            btn.clicked.connect(lambda checked, c=criterion: self.toggle_criterion(c))
            self.update_criterion_button(btn, 0)
            self.criteria_buttons[criterion] = btn
            criteria_flow.addWidget(btn)
        
        layout.addLayout(top_layout)
        layout.addWidget(image_container)
        layout.addWidget(criteria_widget)
        
        self.setLayout(layout)
        
        self.setMinimumWidth(max(210, 2 * button_width + 15))
        
    def load_image(self, size):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            min_size = max(size, 210)
            scaled = pixmap.scaled(min_size, min_size, Qt.AspectRatioMode.KeepAspectRatio, 
                                  Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
            
    def resize_image(self, size):
        self.load_image(size)
        self.setMinimumWidth(max(210, size + 10))
        self.updateGeometry()
        
    def toggle_criterion(self, criterion):
        current = self.criteria[criterion]
        new_value = (current + 2) % 3 - 1
        self.criteria[criterion] = new_value
        self.update_criterion_button(self.criteria_buttons[criterion], new_value)
        self.calculate_score()
        self.positionChanged.emit()
        
    def update_criterion_button(self, btn, value):
        if value == 0:
            btn.setStyleSheet(get_styles().criterion_button_neutral())
        elif value == 1:
            btn.setStyleSheet(get_styles().criterion_button_green())
        else:
            btn.setStyleSheet(get_styles().criterion_button_red())
            
    def calculate_score(self):
        self.total_score = sum(self.criteria.values())
        self.update_score_display()
        
    def update_score_display(self):
        self.score_label.setText(str(self.total_score))
        self.score_label.setStyleSheet(get_styles().score_label())
        
    def set_border_color(self, color):
        if color == "green":
            self.setStyleSheet(get_styles().card_border_green())
        elif color == "red":
            self.setStyleSheet(get_styles().card_border_red())
        else:
            self.setStyleSheet(get_styles().card_style())
    
    def delete_card(self):
        grid_tab = self.get_grid_tab()
        if grid_tab:
            grid_tab.remove_card(self)
        self.deleteLater()
            
    def image_clicked(self, event):
        grid_tab = self.get_grid_tab()
        if grid_tab:
            grid_tab.show_fullscreen_image(self)
    
    def get_grid_tab(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, GridTab):
                return parent
            parent = parent.parent()
        return None
    
    def is_click_on_image(self, pos):
        """Check if click position is on the image label"""
        if self.image_label and self.image_label.pixmap():
            image_rect = self.image_label.geometry()
            return image_rect.contains(pos)
        return False
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
            self.long_press_started = False
            self.press_timer.start(300)
        elif event.button() == Qt.MouseButton.RightButton:
            # Show card details on right-click
            self.show_card_details()
    
    def show_card_details(self):
        """Show card details dialog, closing any existing one first"""
        grid_tab = self.get_grid_tab()
        if not grid_tab:
            return
        
        # Close and delete existing dialog if any
        if hasattr(grid_tab, 'active_details_dialog') and grid_tab.active_details_dialog is not None:
            try:
                grid_tab.active_details_dialog.close()
                grid_tab.active_details_dialog.deleteLater()
            except:
                pass
        
        # Create and show new dialog
        dialog = CardDetailsDialog(self, self.window())
        grid_tab.active_details_dialog = dialog
        dialog.show_near_card()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_timer.stop()
            if not self.long_press_started and self.is_click_on_image(self.drag_start_pos):
                self.image_clicked(event)
            self.long_press_started = False
            self.drag_start_pos = None
    
    def start_drag_operation(self):
        """Called by timer after long press delay"""
        self.long_press_started = True
            
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self.drag_start_pos is None:
            return
        
        if not self.long_press_started:
            if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
                return
        
        self.press_timer.stop()
        self.long_press_started = True
            
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(id(self)))
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.MoveAction)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("ImageCard { border: 3px solid blue; }")
            
    def dragLeaveEvent(self, event):
        self.set_border_color(None)
        
    def dropEvent(self, event):
        self.set_border_color(None)
        source_id = int(event.mimeData().text())
        grid_tab = self.get_grid_tab()
        if grid_tab:
            grid_tab.swap_cards(source_id, id(self))
        event.acceptProposedAction()
        
    def get_data(self):
        return {
            "fileName": os.path.basename(self.image_path),
            "absolutePath": self.image_path,
            "checkpointName": self.checkpoint_name,
            "criteria": self.criteria.copy(),
            "totalScore": self.total_score
        }
    
    def apply_styles(self):
        """Apply current theme styles to card widgets"""
        styles = get_styles()
        self.setStyleSheet(styles.card_style())
        self.close_btn.setStyleSheet(styles.close_button())
        self.checkpoint_label.setStyleSheet(styles.checkpoint_label())
        self.score_label.setStyleSheet(styles.score_label())
        
        # Update all criterion buttons
        for criterion, btn in self.criteria_buttons.items():
            self.update_criterion_button(btn, self.criteria[criterion])
        
        # Update border based on score
        self.set_border_color(None)


class GridTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.checkpoints_list = []
        self.card_size = 210
        self.active_details_dialog = None  # Track active card details dialog
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Controls row 1
        controls1 = QHBoxLayout()
        
        self.close_tab_btn = QPushButton("×")
        self.close_tab_btn.setFixedSize(30, 30)
        self.close_tab_btn.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.close_tab_btn.clicked.connect(self.close_current_tab)
        
        self.options_btn = QPushButton(config.get_text('btn_options'))
        self.options_btn.clicked.connect(self.open_options)
        self.options_btn.setStyleSheet(get_styles().options_button())
        
        self.load_checkpoints_btn = QPushButton(config.get_text('btn_select_folder'))
        self.load_checkpoints_btn.clicked.connect(self.load_checkpoints_folder)
        
        self.load_checkpoints_txt_btn = QPushButton("Checkpoints.txt")
        self.load_checkpoints_txt_btn.clicked.connect(self.load_checkpoints_txt)
        
        self.export_btn = QPushButton(config.get_text('btn_export'))
        self.export_btn.clicked.connect(self.export_grid)
        
        self.import_btn = QPushButton(config.get_text('btn_import'))
        self.import_btn.clicked.connect(self.import_grid)
        
        self.clear_btn = QPushButton(config.get_text('btn_clear'))
        self.clear_btn.setStyleSheet(get_styles().clear_button())
        self.clear_btn.clicked.connect(self.clear_grid)
        
        controls1.addWidget(self.close_tab_btn)
        controls1.addWidget(self.options_btn)
        controls1.addWidget(self.load_checkpoints_btn)
        controls1.addWidget(self.load_checkpoints_txt_btn)
        controls1.addWidget(self.export_btn)
        controls1.addWidget(self.import_btn)
        controls1.addWidget(self.clear_btn)
        controls1.addStretch()
        
        # Controls row 2 - Log and Size slider
        controls2 = QHBoxLayout()
        
        log_label = QLabel("ℹ️ Info :")
        log_label.setStyleSheet("font-weight: bold;")
        
        self.log_label = QLabel("")
        self.log_label.setStyleSheet("color: gray;")
        self.log_label.setMinimumWidth(300)
        
        self.size_label = QLabel(config.get_text('slider_label') + ":")
        
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(210)
        self.size_slider.setMaximum(600)
        self.size_slider.setValue(210)
        self.size_slider.setFixedWidth(150)
        self.size_slider.sliderReleased.connect(self.on_slider_released)
        
        controls2.addWidget(log_label)
        controls2.addWidget(self.log_label)
        controls2.addStretch()
        controls2.addWidget(self.size_label)
        controls2.addWidget(self.size_slider)
        
        # Drag and drop zone
        self.drop_zone = QLabel(config.get_text('drop_zone_text'))
        self.drop_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_zone.setStyleSheet(get_styles().drop_zone())
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.dragEnterEvent = self.drop_zone_drag_enter
        self.drop_zone.dropEvent = self.drop_zone_drop
        self.drop_zone.mousePressEvent = self.drop_zone_click
        
        # Scroll area for cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.close_active_dialog)
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.close_active_dialog)
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        
        main_layout.addLayout(controls1)
        main_layout.addLayout(controls2)
        main_layout.addWidget(self.drop_zone)
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
    
    def open_options(self):
        """Open options dialog"""
        dialog = OptionsDialog(self.get_main_window())
        dialog.exec()
        
    def log(self, message, persistent_callback=None):
        """
        Display a log message for 3 seconds, then optionally show persistent info
        Args:
            message: Message to display
            persistent_callback: Optional function to call after 3s to show persistent info
        """
        self.log_label.setText(message)
        self.log_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        if persistent_callback:
            QTimer.singleShot(3000, persistent_callback)
        else:
            QTimer.singleShot(3000, self.safe_clear_log)
    
    def show_info_persistent(self, text, color="#2196F3"):
        """Display persistent information in the info label"""
        try:
            if self.log_label is not None:
                self.log_label.setText(text)
                self.log_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        except RuntimeError:
            pass

    def safe_clear_log(self):
        """Safely clear log label, handling deleted widgets"""
        try:
            if self.log_label is not None:
                self.log_label.setText("")
        except RuntimeError:
            # Widget has been deleted, ignore
            pass

    def apply_theme(self):
        self.setStyleSheet(get_styles().main_theme())
        self.drop_zone.setStyleSheet(get_styles().drop_zone())
    
    def apply_styles(self):
        """Apply current theme styles to all widgets in this tab"""
        styles = get_styles()
        self.setStyleSheet(styles.main_theme())
        self.drop_zone.setStyleSheet(styles.drop_zone())
        self.options_btn.setStyleSheet(styles.options_button())
        self.clear_btn.setStyleSheet(styles.clear_button())
        
        # Apply styles to all cards
        for card in self.cards:
            card.apply_styles()
        
    def drop_zone_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def drop_zone_drop(self, event):
        files = []
        json_files = []
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                files.append(file_path)
            elif file_path.lower().endswith('.json'):
                json_files.append(file_path)
        
        # Handle JSON import first (only one JSON file at a time)
        if json_files:
            if len(json_files) > 1:
                self.log("⚠️ Multiple JSON files detected. Importing only the first one.")
            self.import_from_file(json_files[0])
        # Then handle images
        elif files:
            self.load_images_from_paths(files)
        
        event.acceptProposedAction()
        
    def drop_zone_click(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images or JSON", "", 
            "Images and JSON (*.png *.jpg *.jpeg *.webp *.json);;Images (*.png *.jpg *.jpeg *.webp);;JSON (*.json);;All Files (*.*)"
        )
        
        if not files:
            return
        
        # Separate images and JSON
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        json_files = [f for f in files if f.lower().endswith('.json')]
        
        # Handle JSON first
        if json_files:
            if len(json_files) > 1:
                self.log("⚠️ Multiple JSON files selected. Importing only the first one.")
            self.import_from_file(json_files[0])
        # Then handle images
        elif image_files:
            self.load_images_from_paths(image_files)
    
    def close_current_tab(self):
        tab_widget = self.get_tab_widget()
        if tab_widget and tab_widget.count() > 1:
            current_index = tab_widget.indexOf(self)
            if current_index >= 0:
                tab_widget.removeTab(current_index)
                self.deleteLater()
        elif tab_widget and tab_widget.count() == 1:
            self.log_label.setText("Can't delete the first tab")
            self.log_label.setStyleSheet("color: yellow; font-weight: bold;")
            QTimer.singleShot(3000, self.safe_clear_log)
        if tab_widget and tab_widget.count() == 1:
            tab_widget.setTabText(0, "A")
    
    def load_checkpoints_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select checkpoints.txt", "", config.get_text('file_filter_txt')
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.checkpoints_list = [line.strip() for line in f if line.strip()]
            self.log(f"Loaded {len(self.checkpoints_list)} checkpoints from txt")
            self.update_existing_card_names()
        except Exception as e:
            self.log(f"Error loading txt: {str(e)}")
    
    def load_checkpoints_folder(self):
        folder = QFileDialog.getExistingDirectory(self, config.get_text('dialog_select_folder'))
        if not folder:
            return
            
        checkpoints = []
        path = Path(folder)
        
        for item in path.rglob("*.safetensors"):
            if item.relative_to(path).parts.__len__() <= 3:
                checkpoints.append(item.stem)
                
        if checkpoints:
            txt_path = Path(folder) / "checkpoints.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                for cp in checkpoints:
                    f.write(cp + '\n')
            self.checkpoints_list = checkpoints
            self.log(f"Loaded {len(checkpoints)} checkpoints, saved to {txt_path}")
            self.update_existing_card_names()
        else:
            self.log("No checkpoints found")
            
    def extract_checkpoint_from_filename(self, filename):
        if not self.checkpoints_list:
            return "unknown"
        for checkpoint in self.checkpoints_list:
            if checkpoint in filename:
                return checkpoint
        return "unknown"
    
    def update_existing_card_names(self):
        """Update checkpoint names of existing cards after loading checkpoint list"""
        updated = 0
        for card in self.cards:
            filename = os.path.basename(card.image_path)
            new_checkpoint = self.extract_checkpoint_from_filename(filename)
            if new_checkpoint != card.checkpoint_name:
                card.checkpoint_name = new_checkpoint
                card.checkpoint_label.setText(new_checkpoint)
                updated += 1
        if updated > 0:
            self.log(f"Updated {updated} card name(s)")
        
    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", 
            config.get_text('file_filter_images')
        )
        
        if files:
            self.load_images_from_paths(files)
            
    def load_images_from_paths(self, files):
        # Get existing image paths to avoid duplicates
        existing_paths = {card.image_path for card in self.cards}
        
        new_images = 0
        duplicates = 0
        
        for file_path in files:
            # Skip if image already loaded
            if file_path in existing_paths:
                duplicates += 1
                continue
                
            filename = os.path.basename(file_path)
            checkpoint = self.extract_checkpoint_from_filename(filename)
            card = ImageCard(file_path, checkpoint, self)
            card.positionChanged.connect(self.update_borders)
            self.cards.append(card)
            new_images += 1
            
        self.refresh_grid()
        
        if new_images > 0:
            total_count = len(self.cards)
            self.log(
                f"Loaded {new_images} new images",
                lambda: self.show_info_persistent(f"{total_count} images")
            )
        if duplicates > 0:
            self.log(f"Skipped {duplicates} duplicate(s)")
        if new_images == 0 and duplicates == 0:
            self.log("No images to load")
        
    def refresh_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        for i in range(self.grid_layout.columnCount()):
            self.grid_layout.setColumnStretch(i, 0)
                
        actual_card_width = max(210, self.card_size) + 20
        cols = max(1, self.scroll_area.width() // actual_card_width)
        for idx, card in enumerate(self.cards):
            row = idx // cols
            col = idx % cols
            self.grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self.grid_layout.setColumnStretch(col, 0)
        
        if cols > 0:
            self.grid_layout.setColumnStretch(cols, 1)
            
        self.update_borders()
        
    def resize_cards(self, size):
        self.card_size = size
        for card in self.cards:
            card.resize_image(size)
        self.refresh_grid()
    
    def on_slider_released(self):
        size = self.size_slider.value()
        self.resize_cards(size)
        
    def update_borders(self):
        if not self.cards:
            return
            
        scores = [card.total_score for card in self.cards]
        max_score = max(scores)
        min_score = min(scores)
        
        for card in self.cards:
            if card.total_score == max_score and max_score != min_score:
                card.set_border_color("green")
            elif card.total_score == min_score and max_score != min_score:
                card.set_border_color("red")
            else:
                card.set_border_color(None)
                
    def remove_card(self, card):
        if card in self.cards:
            self.cards.remove(card)
        self.refresh_grid()
        # Update persistent info after card removal
        if self.cards:
            self.show_info_persistent(f"{len(self.cards)} images")
        else:
            self.safe_clear_log()
        
    def swap_cards(self, source_id, target_id):
        source_card = None
        target_card = None
        
        for card in self.cards:
            if id(card) == source_id:
                source_card = card
            if id(card) == target_id:
                target_card = card
                
        if source_card and target_card:
            idx_source = self.cards.index(source_card)
            idx_target = self.cards.index(target_card)
            
            self.cards.pop(idx_source)
            
            if idx_source < idx_target:
                insert_pos = idx_target
            else:
                insert_pos = idx_target
            
            self.cards.insert(insert_pos, source_card)
            
            self.refresh_grid()
            
    def clear_grid(self):
        for card in self.cards[:]:
            card.deleteLater()
        self.cards.clear()
        self.refresh_grid()
        # Clear persistent info when clearing grid
        self.log(config.get_text('msg_loaded'))
        
    def export_grid(self):
        if not self.cards:
            self.log(config.get_text('msg_no_images'))
            return
            
        tab_widget = self.get_tab_widget()
        tab_index = tab_widget.indexOf(self) if tab_widget else 0
        tab_name = tab_widget.tabText(tab_index) if tab_widget else "A"
        
        data = {
            "images": [card.get_data() for card in self.cards]
        }
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"grid-{tab_name}_{timestamp}.json"
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, config.get_text('dialog_export_title'), filename, config.get_text('file_filter_json')
        )
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(config.get_text('msg_exported'))
            
    def import_from_file(self, file_path):
        """Import grid from a JSON file path"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check import mode
            import_mode = config.get('import_mode')
            
            if import_mode == 'replace':
                # Replace: clear existing cards first
                self.clear_grid()
            # else: add mode - keep existing cards
            
            # Get existing paths to avoid duplicates in add mode
            existing_paths = {card.image_path for card in self.cards} if import_mode == 'add' else set()
            
            # Get source JSON filename for tracking
            source_json_name = os.path.basename(file_path)
            
            added_count = 0
            missing_count = 0
            for img_data in data.get("images", []):
                if os.path.exists(img_data["absolutePath"]):
                    # Skip duplicates in add mode
                    if import_mode == 'add' and img_data["absolutePath"] in existing_paths:
                        continue
                        
                    card = ImageCard(
                        img_data["absolutePath"],
                        img_data["checkpointName"],
                        self,
                        source_json=source_json_name
                    )
                    card.criteria = img_data["criteria"]
                    card.total_score = img_data["totalScore"]
                    card.calculate_score()
                    card.positionChanged.connect(self.update_borders)
                    self.cards.append(card)
                    added_count += 1
                else:
                    missing_count += 1
                    
            self.refresh_grid()
            
            # Get filename for persistent display
            filename = os.path.basename(file_path)
            total_count = len(self.cards)
            
            if import_mode == 'add':
                msg = f"{config.get_text('msg_imported')}: +{added_count} images (total: {len(self.cards)})"
            else:
                msg = f"{config.get_text('msg_imported')}: {len(self.cards)} images"
            
            if missing_count > 0:
                msg += f" ({missing_count} missing files skipped)"
            
            # Show log for 3s, then show persistent info with filename
            self.log(
                msg,
                lambda: self.show_info_persistent(f"{filename} - {total_count} images")
            )
            
        except Exception as e:
            self.log(f"Import error: {str(e)}")
    
    def import_grid(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, config.get_text('dialog_import_title'), "", config.get_text('file_filter_json')
        )
        
        if not file_path:
            return
        
        self.import_from_file(file_path)
            
    def get_tab_widget(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, QTabWidget):
                return parent
            parent = parent.parent()
        return None
    
    def get_main_window(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None
    
    def close_active_dialog(self):
        """Close the active details dialog if any"""
        if hasattr(self, 'active_details_dialog') and self.active_details_dialog is not None:
            try:
                self.active_details_dialog.close()
            except:
                pass
            self.active_details_dialog = None
    
    def reposition_active_dialog(self):
        """Reposition the active details dialog if any"""
        if hasattr(self, 'active_details_dialog') and self.active_details_dialog is not None:
            try:
                if self.active_details_dialog.isVisible():
                    self.active_details_dialog.show_near_card()
            except:
                pass
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_active_dialog()  # Reposition popup on resize
        if hasattr(self, 'cards') and self.cards:
            QTimer.singleShot(100, self.refresh_grid)
    
    def refresh_ui_texts(self):
        """Refresh all UI text elements after language change"""
        self.options_btn.setText(config.get_text('btn_options'))
        self.load_checkpoints_btn.setText(config.get_text('btn_select_folder'))
        self.export_btn.setText(config.get_text('btn_export'))
        self.import_btn.setText(config.get_text('btn_import'))
        self.clear_btn.setText(config.get_text('btn_clear'))
        self.size_label.setText(config.get_text('slider_label') + ":")
        self.drop_zone.setText(config.get_text('drop_zone_text'))
        
    def show_fullscreen_image(self, card):
        dialog = FullscreenDialog(card, self)
        dialog.exec()


class FullscreenDialog(QDialog):
    def __init__(self, card, grid_tab, parent=None):
        super().__init__(parent)
        self.card = card
        self.grid_tab = grid_tab
        self.comparison_card = None
        self.comparison_pixmap = None
        self.main_pixmap = QPixmap(card.image_path)
        self.split_position = 0.5
        self.dragging_split = False
        self.image_x_offset = 0
        self.image_width = 0
        
        self.current_card_index = 0
        for i, c in enumerate(grid_tab.cards):
            if c == card:
                self.current_card_index = i
                break
        
        self.setWindowTitle("Fullscreen View")
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.showFullScreen()
        
        self.setStyleSheet(get_styles().fullscreen_background())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top controls
        top_bar = QHBoxLayout()
        
        close_btn = QPushButton("✕ ESC")
        close_btn.setFixedSize(80, 40)
        close_btn.setStyleSheet(get_styles().fullscreen_close_button())
        close_btn.clicked.connect(self.close)
        
        grid_label = QLabel(config.get_text('fullscreen_compare'))
        grid_label.setStyleSheet(get_styles().fullscreen_label())
        
        self.grid_combo = QComboBox()
        self.grid_combo.setMinimumHeight(30)
        self.grid_combo.setStyleSheet(get_styles().fullscreen_combo())
        
        main_window = self.get_main_window()
        current_tab_index = 0
        if main_window:
            current_tab_index = main_window.tabs.indexOf(grid_tab)
            for i in range(main_window.tabs.count()):
                tab_name = main_window.tabs.tabText(i)
                if i == current_tab_index:
                    self.grid_combo.addItem(f"{tab_name} (current)", i)
                else:
                    self.grid_combo.addItem(tab_name, i)
            for idx in range(self.grid_combo.count()):
                if self.grid_combo.itemData(idx) == current_tab_index:
                    self.grid_combo.setCurrentIndex(idx)
                    break
        else:
            self.grid_combo.addItem(f"Grid A (current)", 0)
        
        top_bar.addWidget(close_btn)
        top_bar.addStretch()
        top_bar.addWidget(grid_label)
        top_bar.addWidget(self.grid_combo)
        top_bar.addWidget(QLabel("   "))  # Small spacer
        
        # Image info labels
        info_layout = QHBoxLayout()
        self.info_label = QLabel()
        self.info_label.setStyleSheet(get_styles().fullscreen_info_selectable())
        self.info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.info_label2 = QLabel()
        self.info_label2.setStyleSheet(get_styles().fullscreen_info_selectable())
        self.info_label2.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.info_label2.setVisible(False)
        
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        info_layout.addWidget(self.info_label2)
        
        # Image display
        self.image_container = QLabel()
        self.image_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_container.setStyleSheet(get_styles().image_container())
        self.image_container.mousePressEvent = self.mouse_press_on_image
        self.image_container.mouseMoveEvent = self.mouse_move_on_image
        self.image_container.mouseReleaseEvent = self.mouseReleaseEvent
        self.image_container.paintEvent = self.paint_image
        
        layout.addLayout(top_bar)
        layout.addWidget(self.image_container, stretch=1)
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
        self.update_info_label()
        
        self.grid_combo.currentIndexChanged.connect(self.on_grid_changed)
    
    def paint_image(self, event):
        if self.main_pixmap.isNull():
            return
        
        painter = QPainter(self.image_container)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        container_rect = self.image_container.rect()
        
        if not self.comparison_pixmap:
            scaled = self.main_pixmap.scaled(
                container_rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (container_rect.width() - scaled.width()) // 2
            y = (container_rect.height() - scaled.height()) // 2
            self.image_x_offset = x
            self.image_width = scaled.width()
            painter.drawPixmap(x, y, scaled)
        else:
            max_width = container_rect.width()
            max_height = container_rect.height()
            
            scaled1 = self.main_pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            scaled2 = self.comparison_pixmap.scaled(
                max_width, max_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            display_width = min(scaled1.width(), scaled2.width())
            display_height = min(scaled1.height(), scaled2.height())
            
            x = (container_rect.width() - display_width) // 2
            y = (container_rect.height() - display_height) // 2
            
            self.image_x_offset = x
            self.image_width = display_width
            
            split_x = int(x + display_width * self.split_position)
            
            left_rect = QRect(0, 0, int(display_width * self.split_position), display_height)
            painter.drawPixmap(x, y, scaled1, 0, 0, left_rect.width(), display_height)
            
            right_width = display_width - left_rect.width()
            painter.drawPixmap(
                split_x, y,
                scaled2,
                int(scaled2.width() * self.split_position), 0,
                right_width, display_height
            )
            
            painter.setPen(QPen(QColor(get_styles().COLORS['text_white']), 3))
            painter.drawLine(split_x, y, split_x, y + display_height)
            
            handle_y = y + display_height // 2
            painter.setBrush(QColor(get_styles().COLORS['blue']))
            painter.drawEllipse(split_x - 15, handle_y - 15, 30, 30)
            painter.setPen(QPen(QColor(get_styles().COLORS['text_white']), 2))
            painter.drawLine(split_x - 8, handle_y, split_x + 8, handle_y)
        
        painter.end()
    
    def get_main_window(self):
        widget = self.grid_tab
        while widget:
            if isinstance(widget, MainWindow):
                return widget
            widget = widget.parent()
        return None
    
    def on_grid_changed(self, index):
        main_window = self.get_main_window()
        if not main_window:
            return
        
        selected_tab_index = self.grid_combo.itemData(index)
        if selected_tab_index is None:
            return
            
        selected_tab = main_window.tabs.widget(selected_tab_index)
        current_tab_index = main_window.tabs.indexOf(self.grid_tab)
        
        if selected_tab_index == current_tab_index or not selected_tab or not hasattr(selected_tab, 'cards'):
            self.info_label2.setVisible(False)
            self.comparison_card = None
            self.comparison_pixmap = None
            self.image_container.update()
        else:
            cards = selected_tab.cards
            if cards:
                self.comparison_card = cards[0]
                
                pixmap2 = QPixmap(self.comparison_card.image_path)
                if not pixmap2.isNull():
                    self.comparison_pixmap = pixmap2
                
                self.info_label2.setVisible(True)
                self.update_info_label()
                self.split_position = 0.5
                self.image_container.update()
    
    def mouse_press_on_image(self, event):
        if self.comparison_pixmap:
            self.dragging_split = True
            self.update_split_from_mouse(event.pos().x())
    
    def mouse_move_on_image(self, event):
        if self.comparison_pixmap and (self.dragging_split or event.buttons() & Qt.MouseButton.LeftButton):
            self.dragging_split = True
            self.update_split_from_mouse(event.pos().x())
    
    def update_split_from_mouse(self, mouse_x):
        if self.image_width > 0:
            relative_x = mouse_x - self.image_x_offset
            self.split_position = max(0.0, min(1.0, relative_x / self.image_width))
            self.image_container.update()
    
    def mouseReleaseEvent(self, event):
        self.dragging_split = False
    
    def update_info_label(self):
        info1 = f"{self.card.checkpoint_name} - {os.path.basename(self.card.image_path)}"
        self.info_label.setText(info1)
        
        if self.comparison_card:
            info2 = f"{self.comparison_card.checkpoint_name} - {os.path.basename(self.comparison_card.image_path)}"
            self.info_label2.setText(info2)
    
    def show_previous_image(self):
        if self.current_card_index > 0:
            self.current_card_index -= 1
            self.load_card_at_index(self.current_card_index)
            if self.comparison_card:
                self.load_comparison_at_index(self.current_card_index)
    
    def show_next_image(self):
        if self.current_card_index < len(self.grid_tab.cards) - 1:
            self.current_card_index += 1
            self.load_card_at_index(self.current_card_index)
            if self.comparison_card:
                self.load_comparison_at_index(self.current_card_index)
    
    def load_card_at_index(self, index):
        if 0 <= index < len(self.grid_tab.cards):
            self.card = self.grid_tab.cards[index]
            
            pixmap = QPixmap(self.card.image_path)
            if not pixmap.isNull():
                self.main_pixmap = pixmap
                self.image_container.update()
            
            self.update_info_label()
    
    def load_comparison_at_index(self, index):
        main_window = self.get_main_window()
        if not main_window:
            return
        
        selected_index = self.grid_combo.currentIndex()
        selected_tab_index = self.grid_combo.itemData(selected_index)
        if selected_tab_index is None:
            return
        
        selected_tab = main_window.tabs.widget(selected_tab_index)
        if selected_tab and hasattr(selected_tab, 'cards') and selected_tab.cards:
            comp_index = min(index, len(selected_tab.cards) - 1)
            self.comparison_card = selected_tab.cards[comp_index]
            
            pixmap2 = QPixmap(self.comparison_card.image_path)
            if not pixmap2.isNull():
                self.comparison_pixmap = pixmap2
                self.image_container.update()
            
            self.update_info_label()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Left:
            self.show_previous_image()
        elif event.key() == Qt.Key.Key_Right:
            self.show_next_image()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.get_text('window_title'))
        self.setGeometry(100, 100, 1400, 900)
        
        styles = get_styles()
        self.setStyleSheet(get_styles().main_window())
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        
        tab_bar = self.tabs.tabBar()
        
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)
        
        self.add_tab_btn = QPushButton("+")
        self.add_tab_btn.setFixedSize(30, 30)
        styles = get_styles()
        self.add_tab_btn.setStyleSheet(get_styles().add_tab_button())
        self.add_tab_btn.clicked.connect(self.add_tab)
        
        self.remove_all_btn = QPushButton("-")
        self.remove_all_btn.setFixedSize(30, 30)
        self.remove_all_btn.setStyleSheet(get_styles().remove_tab_button())
        self.remove_all_btn.clicked.connect(self.remove_all_tabs)
        
        button_layout.addWidget(self.add_tab_btn)
        button_layout.addWidget(self.remove_all_btn)
        button_widget.setLayout(button_layout)
        
        self.tabs.setCornerWidget(button_widget, Qt.Corner.TopRightCorner)
        
        layout.addWidget(self.tabs)
        central.setLayout(layout)
        
        self.add_tab()
    
    def add_tab(self):
        tab_count = self.tabs.count()
        if tab_count >= 26:
            return
            
        letter = chr(65 + tab_count)
        grid_tab = GridTab()
        tab_index = self.tabs.addTab(grid_tab, letter)
        
        self.tabs.setCurrentIndex(tab_index)
        
        if self.tabs.count() == 1:
            self.tabs.setTabText(0, "A")
            
    def remove_all_tabs(self):
        while self.tabs.count() > 0:
            widget = self.tabs.widget(0)
            self.tabs.removeTab(0)
            widget.deleteLater()
        self.add_tab()
    
    def refresh_ui_texts(self):
        """Refresh all UI texts after language change"""
        self.setWindowTitle(config.get_text('window_title'))
        
        # Refresh all tabs
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'refresh_ui_texts'):
                tab.refresh_ui_texts()
    
    def apply_styles(self):
        """Apply current theme styles to window and all tabs"""
        styles = get_styles()
        self.setStyleSheet(get_styles().main_window())
        self.add_tab_btn.setStyleSheet(get_styles().add_tab_button())
        self.remove_all_btn.setStyleSheet(get_styles().remove_tab_button())
        
        # Apply styles to all tabs
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'apply_styles'):
                tab.apply_styles()
    
    def reposition_all_dialogs(self):
        """Reposition all active detail dialogs in all tabs"""
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if hasattr(tab, 'reposition_active_dialog'):
                tab.reposition_active_dialog()
    
    def moveEvent(self, event):
        """Reposition popups when window is moved"""
        super().moveEvent(event)
        self.reposition_all_dialogs()
    
    def resizeEvent(self, event):
        """Reposition popups when window is resized"""
        super().resizeEvent(event)
        self.reposition_all_dialogs()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
