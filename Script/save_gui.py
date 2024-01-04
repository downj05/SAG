import os
import json
from PyQt5 import QtWidgets

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

def save_setting(key, value):
    print(f"Saving setting: {key} = {value}")
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
    settings[key] = value
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_setting(key):
    # Create the settings file if it doesn't exist
    if not os.path.exists(SETTINGS_FILE):
        print("Creating settings file")
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({}, f, indent=4)
    # Load the settings file
    with open(SETTINGS_FILE, 'r') as f:
        settings = json.load(f)
        if 'webhookUrlTextBox' in key:
            # censor the webhook urlI
            # replace second half of the url with asterisks
            print(f"Loading setting: {key} = {settings.get(key, None)[:30]}{'*' * 30}")
            # print(f"Loading setting: {key} = {settings.get(key, '')}")
            
        else:
            print(f"Loading setting: {key} = {settings.get(key, None)}")
    return settings.get(key, None)


def init(widget: QtWidgets.QWidget):
    """
    Load the settings from the settings.json file and apply them to the widgets
    Assigns the save_setting function to the widgets respective signals
    """
    val = load_setting(widget.objectName())

    # Checkbox & GroupBox
    if isinstance(widget, (QtWidgets.QCheckBox, QtWidgets.QGroupBox)):
        # Default to current value if the setting doesn't exist
        if val is None:
            val = widget.isChecked()
        widget.setChecked(val)
        if isinstance(widget, QtWidgets.QGroupBox):
            widget.toggled.connect(lambda: save_setting(widget.objectName(), widget.isChecked()))
            return
        
        widget.stateChanged.connect(lambda: save_setting(widget.objectName(), widget.isChecked()))

    
    # LineEdit
    elif isinstance(widget, QtWidgets.QLineEdit):
        if val is None:
            val = widget.text()

        widget.setText(val)
        widget.textChanged.connect(lambda: save_setting(widget.objectName(), widget.text()))

    # Slider
    elif isinstance(widget, QtWidgets.QSlider):
        if val is None:
            val = widget.value()

        widget.setValue(val)
        widget.sliderReleased.connect(lambda: save_setting(widget.objectName(), widget.value()))
    
    # SpinBox
    elif isinstance(widget, QtWidgets.QSpinBox):
        if val is None:
            val = widget.value()

        widget.setValue(val)
        widget.valueChanged.connect(lambda: save_setting(widget.objectName(), widget.value()))