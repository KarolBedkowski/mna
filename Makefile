RESOURCE_DIR = data/gui
COMPILED_DIR = mna/gui
PLUGINS_DIR = mna/plugins

UI_FILES = $(wildcard ${RESOURCE_DIR}/*.ui)
RESOURCES = $(wildcard ${RESOURCE_DIR}/*.qrc)

PYUIC = pyuic4
PYRCC = pyrcc4

COMPILED_UI = $(UI_FILES:$(RESOURCE_DIR)/%.ui=$(COMPILED_DIR)/ui_%.py)
COMPILED_RESOURCES = $(RESOURCES:$(RESOURCE_DIR)/%.qrc=$(COMPILED_DIR)/%_rc.py)

PLUGIN_RESOURCES = $(shell find $(PLUGINS_DIR) -type f -name '*.qrc')
PLUGIN_COMPILED_RESOURCES = $(patsubst %.qrc, %_rc.py, $(PLUGIN_RESOURCES))

PLUGIN_UI_FILES = $(shell find $(PLUGINS_DIR) -type f -name '*.ui')
PLUGIN_COMPILED_UI = $(patsubst %.ui, %_ui.py, $(PLUGIN_UI_FILES))


all : resources ui plugin_resources plugin_ui

resources : $(COMPILED_RESOURCES)

ui : $(COMPILED_UI)

$(COMPILED_DIR)/ui_%.py : $(RESOURCE_DIR)/%.ui
	$(PYUIC) $< -o $@

$(COMPILED_DIR)/%_rc.py : $(RESOURCE_DIR)/%.qrc
	$(PYRCC) $< -o $@

plugin_resources: $(PLUGIN_COMPILED_RESOURCES)

$(PLUGINS_DIR)/%_rc.py : $(PLUGINS_DIR)/%.qrc
	$(PYRCC) $< -o $@

plugin_ui : $(PLUGIN_COMPILED_UI)

$(PLUGINS_DIR)/%_ui.py : $(PLUGINS_DIR)/%.ui
	$(PYUIC) $< -o $@

clean :
	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES)
	$(RM) $(PLUGIN_COMPILED_UI) $(PLUGIN_COMPILED_UI_COMPILED_RESOURCES)
	find $(RESOURCE_DIR) -type f \( -name '*.pyc' -or -name '*.pyo' \) -delete
