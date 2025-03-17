from PyQt5.QtWidgets import QMessageBox

def show_alert(parent, usage_percent):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("High Memory Usage")
    msg.setText(f"Memory usage is at {usage_percent}%.")
    msg.exec_()
