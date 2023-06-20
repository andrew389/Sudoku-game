from PyQt5.QtWidgets import QStackedWidget, QMessageBox, QFrame, QGridLayout, QFileDialog, QLineEdit, QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt, QTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from Sud_Boards import easy, medium, hard
from build.Debug.sudoku import read_file, solve, is_valid_sudoku

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        self.main_menu_window = MainMenuWindow()
        self.main_menu_window.show()


class MainMenuWindow(QMainWindow): # Головне меню
    def __init__(self):
        super(MainMenuWindow, self).__init__()
        self.setWindowTitle("Гра Судоку")
        self.setGeometry(10, 10, 500, 400)

        screen_geometry = QApplication.desktop().screenGeometry()

        # Центрування екрану
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.main_menu_widget = QWidget()
        self.about_widget = QWidget()

        self.stacked_widget.addWidget(self.main_menu_widget)
        self.stacked_widget.addWidget(self.about_widget)

        self.setup_main_menu()
        self.setup_about_content()

        self.stacked_widget.setCurrentWidget(self.main_menu_widget)

    def setup_main_menu(self):
        self.play_button = QPushButton("Грати")
        self.about_button = QPushButton("Про гру")
        self.quit_button = QPushButton("Вийти")

        self.layout_main_menu = QVBoxLayout()
        self.main_menu_widget.setLayout(self.layout_main_menu)

        self.layout_main_menu.addWidget(self.play_button)
        self.layout_main_menu.addWidget(self.about_button)
        self.layout_main_menu.addWidget(self.quit_button)

        self.play_button.setStyleSheet("QPushButton { font-size: 24px; padding: 10px 20px; }")
        self.about_button.setStyleSheet("QPushButton { font-size: 24px; padding: 10px 20px; }")
        self.quit_button.setStyleSheet("QPushButton { font-size: 24px; padding: 10px 20px; background-color: red; color: white; }")

        self.play_button.clicked.connect(self.show_sudoku_game)
        self.about_button.clicked.connect(self.show_about_content)
        self.quit_button.clicked.connect(QApplication.quit)

    def setup_about_content(self):
        self.layout_about = QVBoxLayout()
        self.about_widget.setLayout(self.layout_about)

        self.about_label = QLabel("Гра ""Судоку""\n\nВерсія: 1.0\nРозробив: Кабанов Андрій")
        self.about_label.setStyleSheet("QLabel { font-size: 24px; padding: 20px; }")
        self.layout_about.addWidget(self.about_label)

        self.back_button = QPushButton("Вернутися в меню")
        self.back_button.setStyleSheet("QPushButton { font-size: 24px; padding: 10px 20px; }")
        self.layout_about.addWidget(self.back_button)

        self.back_button.clicked.connect(self.show_main_menu)

    def show_sudoku_game(self):
        self.hide()
        self.sudoku_game_window = MainWindow()
        self.sudoku_game_window.show()

    def show_about_content(self):
        self.stacked_widget.setCurrentWidget(self.about_widget)

    def show_main_menu(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_widget)


class MainWindow(QMainWindow): #Вікно з грою
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Гра Судоку")
        self.setGeometry(10, 10, 500, 500)

        screen_geometry = QApplication.desktop().screenGeometry()

        # Центрування екрану
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        self.field = SudokuFieldWidget()  
        self.field.update_difficulty("easy")
        self.buttons = ButtonWidget(self.field)  

        self.main_layout.addWidget(self.field)
        self.main_layout.addWidget(self.buttons)

        self.buttons.difficulty_changed.connect(self.field.update_difficulty)
        self.buttons.file_opened.connect(self.handle_file_opened)

    def handle_file_opened(self, matrix):
        self.field.update_matrix(matrix)


class SudokuFieldWidget(QWidget): # Поле Судоку
    validation_failed = pyqtSignal() # Сигнал для валідації введених чисел

    def __init__(self):
        super(SudokuFieldWidget, self).__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.text_fields = []
        self.current_cell = None  # Поточна комірка

        font = QFont("Arial", 16)

        for i in range(9):
            for j in range(9):
                text_field = QLineEdit()
                text_field.setFixedWidth(50)
                text_field.setFixedHeight(50)
                text_field.setAlignment(Qt.AlignCenter)
                text_field.setStyleSheet("QLineEdit { border: 1px solid #778899; }")

                text_field.setFont(font)
                text_field.mousePressEvent = self.create_mouse_press_event(text_field)  # Встановлюємо обробник події натискання миші
                self.layout.addWidget(text_field, i, j)

                # Встановлюємо обробник події textChanged для валідації чисел
                text_field.textChanged.connect(self.validate_number)

                self.text_fields.append(text_field)

        self.setStyleSheet("QWidget { background-color: transparent; }")
        self.layout.setSpacing(0)  # Встановлюємо отступи між комірками 0

        # Додаємо ліннії до квадратів 3х3
        for i in range(3, 9, 3):
            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setLineWidth(3)
            line.setStyleSheet("QFrame { color: black; }")
            self.layout.addWidget(line, i - 1, 0, 2, 9)

        for j in range(3, 9, 3):
            line = QFrame(self)
            line.setFrameShape(QFrame.VLine)
            line.setLineWidth(3)
            line.setStyleSheet("QFrame { color: black; }")
            self.layout.addWidget(line, 0, j, 9, 1)

    def create_mouse_press_event(self, text_field):
        def mouse_press_event(event):
            if self.current_cell:
                self.remove_highlight()
            self.current_cell = text_field
            self.highlight_selected()
        return mouse_press_event

    def highlight_selected(self):
        row, col = self.get_current_cell_position()
        number = self.current_cell.text()

        # Підсвічуємо ячейи всередині квадрата та лінії з однаковими числами
        for i in range(9):
            for j in range(9):
                cell = self.text_fields[i * 9 + j]
                cell_number = cell.text()
                if cell_number.isdigit() and number.isdigit() and int(cell_number) == int(number):
                    self.highlight_cell(cell, "#DEF7FE")  # Підсвічування блакитним кольором для однакових чисел

                if i != row and j == col:
                    self.highlight_cell(cell)
                if i == row and j != col:
                    self.highlight_cell(cell)

                square_row = i // 3
                square_col = j // 3
                if square_row * 3 <= row < (square_row + 1) * 3 and square_col * 3 <= col < (square_col + 1) * 3:
                    self.highlight_cell(cell)

        # Змінюємо колір вибранної комірки
        self.current_cell.setStyleSheet("QLineEdit { background-color: #DEF7FE; border: 1px solid #778899; }")

    def highlight_cell(self, cell, color="lightgray"):
        cell.setStyleSheet(f"QLineEdit {{ background-color: {color}; border: 1px solid #778899; }}")

    def remove_highlight(self):
        for text_field in self.text_fields:
            text_field.setStyleSheet("QLineEdit { background-color: transparent; border: 1px solid #778899; }")

    def get_current_cell_position(self):
        index = self.text_fields.index(self.current_cell)
        row = index // 9
        col = index % 9
        return row, col

    def update_matrix(self, matrix):
        # Очищуємо попередні значення в матриці
        for text_field in self.text_fields:
            text_field.clear()

        # Встановлюємо числа в поля для вводу
        for i in range(9):
            for j in range(9):
                text_field = self.text_fields[i * 9 + j]
                number = matrix[i][j]
                if number != 0:
                    text_field.setText(str(number))
        
    def update_difficulty(self, difficulty):
        if difficulty == "easy":
            matrix = easy

        elif difficulty == "medium":
            matrix = medium
            
        elif difficulty == "hard":
            matrix = hard
                
        self.update_matrix(matrix)

    def get_matrix(self):
        matrix = []
        for i in range(9):
            row = []
            for j in range(9):
                text_field = self.text_fields[i * 9 + j]
                number = int(text_field.text()) if text_field.text().isdigit() else 0
                row.append(number)
            matrix.append(row)
        return matrix
    
    def validate_number(self):
        sender = self.sender()  # Отримуємо об'єкт QLineEdit відправивший сигнал
        number = sender.text()
        curr_board = self.get_matrix()

        if not number.isdigit() or int(number) < 1 or int(number) > 9:
            sender.setText("")

        elif not is_valid_sudoku(curr_board):
            self.validation_failed.emit()
      

class ButtonWidget(QWidget): # Кнопки

    difficulty_changed = pyqtSignal(str) # сигнал для змінення складності
    file_opened = pyqtSignal(list) # сигнал, для передачі зчитаної матриці з файлу

    def __init__(self, text_fields):
        super(ButtonWidget, self).__init__()

        self.text_fields = text_fields

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.timer_label = QLabel("Час:")
        self.amount_of_errors_label = QLabel("Кількість помилок:")
        self.amount_of_errors = 0 

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItem("easy", 0)
        self.difficulty_combo.addItem("medium", 1)
        self.difficulty_combo.addItem("hard", 2)
        self.difficulty_combo.currentIndexChanged.connect(self.change_difficulty)

        self.read_file_button = QPushButton("Зчитати файл")
        self.read_file_button.clicked.connect(self.open_file)

        self.solve_button = QPushButton("Вирішити судоку")
        self.solve_button.clicked.connect(self.solve_board)

        self.restart_button = QPushButton("Почати наново")
        self.restart_button.clicked.connect(self.restart_board)

        self.check_sudoku = QPushButton("Перевірити поле")
        self.check_sudoku.clicked.connect(self.check_field)

        self.layout.addWidget(self.timer_label)
        self.layout.addWidget(self.amount_of_errors_label)
        self.layout.addWidget(self.difficulty_combo)
        self.layout.addWidget(self.read_file_button)
        self.layout.addWidget(self.solve_button)
        self.layout.addWidget(self.restart_button)
        self.layout.addWidget(self.check_sudoku)
        self.layout.addStretch(1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_label)
        self.timer.start(1000)  # Оновлення кожну секунду

        self.time = QTime(0, 0)  # Початкове значення

        self.update_timer_label()
        self.update_amount_of_errors_label()

        self.text_fields.validation_failed.connect(self.handle_validation_failed)

    def update_timer_label(self):
        self.time = self.time.addSecs(1)  # Збільшуємо на 1 сек.
        formatted_time = self.time.toString('hh:mm:ss') 
        self.timer_label.setText(f"Час: {formatted_time}")
    
    def update_amount_of_errors_label(self):
        self.amount_of_errors_label.setText(f"Кількість помилок: {self.amount_of_errors}/3")

    def handle_validation_failed(self):
        if self.amount_of_errors == 2:
            # Остання помилка - програли
            QMessageBox.information(self, "Гру завершено", "Ви програли!")
            QApplication.quit()
        else:
            # Збільшуємо лічильник помилок
            self.amount_of_errors += 1
            self.update_amount_of_errors_label()

    def solve_board(self):
        solution = self.text_fields.get_matrix()
        if is_valid_sudoku(solution):
            solution = solve(solution)
            self.text_fields.update_matrix(solution)
        else:
            QMessageBox.information(self, "Попередження", "Введіть корректні дані, для рішення судоку!")

    def get_current_difficulty(self):
        current_difficulty = self.difficulty_combo.currentText()
        return current_difficulty

    def restart_board(self):
        current_difficulty = self.get_current_difficulty()
        self.text_fields.update_difficulty(current_difficulty)
        self.time = QTime(0, 0)
        self.amount_of_errors = 0
        self.update_amount_of_errors_label()
        self.update_timer_label()

    def check_field(self):
        current_board = self.text_fields.get_matrix()
        
        if is_valid_sudoku(current_board):
            QMessageBox.information(self, "Інформація", "Поле є правильним")
        else:
            QMessageBox.information(self, "Інформація", "Поле не є правильним")

    def change_difficulty(self, idx):
        if idx == 0:
            self.difficulty_changed.emit("easy")
        elif idx == 1:
            self.difficulty_changed.emit("medium")
        else:
            self.difficulty_changed.emit("hard")

    def open_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Відкрити файл", "", "Text Files (*.txt)")

        if file_path:
            board = read_file(file_path)
            self.file_opened.emit(board)