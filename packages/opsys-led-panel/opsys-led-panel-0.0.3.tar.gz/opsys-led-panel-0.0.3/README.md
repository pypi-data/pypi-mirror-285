# README

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for?

- This repository is a part of opsys automation infrastructure
- This repository is LED Panel controller implementation for LED Panel device

### How do I get set up?

- pip install opsys-led-panel

### Unit Testing

- python -m unittest -v

### Usage Example

```
from opsys_led_panel.led_panel_controller import LedPanelController

led_panel = LedPanelController()

led_panel.connect()
led_panel.set_program(program_number=5)
led_panel.disconnect()
```
