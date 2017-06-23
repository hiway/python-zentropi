
from uzentropi import Agent

agent = Agent('microzen', '6d150905a24d464996fbe94ce57b629f')

from machine import Pin
PINS = {
    12: {'number': 12, 'mode': Pin.OUT, 'value': 0},
    13: {'number': 13, 'mode': Pin.OUT, 'value': 0},
    15: {'number': 15, 'mode': Pin.OUT, 'value': 0},
}

MODES = {
    'out': Pin.OUT,
    'in': Pin.IN,
}


def validate_mode(event):
    mode_ = event.data['mode'].lower().strip()
    if mode_ not in MODES:
        agent.emit('{}_error'.format(event.name),
                   data={'text': 'Modes available: {}'.format(','.join(MODES.keys()))})
        return
    mode = MODES[mode_]
    return mode


def validate_pin(event):
    pin_ = int(event.data['pin'])
    if pin_ not in PINS:
        agent.emit('{}_error'.format(event.name),
                   data={'text': 'Pins available: {}'.format(','.join([str(k) for k in PINS.keys()]))})
        return
    pin = PINS[pin_]
    return pin


def validate_value(event):
    value_ = event.data['value'].strip()
    if value_ == 'off':
        value = 0
    elif value_ == 'on':
        value = 1
    else:
        try:
            value = int(value_)
            assert value in [0, 1]
        except (ValueError, AssertionError):
            agent.emit('{}_error'.format(event.name),
                       data={'text': 'Invalid value {}. Try: "on", "off", 0 or 1'.format(value_)})
            return
    return value


@agent.on_event('esp_gpio_mode')
def esp_gpio_on(event):
    mode = validate_mode(event)
    pin = validate_pin(event)
    value = validate_value(event)
    if not pin:
        return
    pin['mode'] = mode
    pin['value'] = value
    pin_obj = Pin(pin['number'], mode)
    pin_obj.value(value)


@agent.on_event('esp_gpio_on')
def esp_gpio_on(event):
    pin = validate_pin(event)
    if not pin:
        return
    pin_obj = Pin(pin['number'], pin['mode'])
    pin_obj.value(1)


@agent.on_event('esp_gpio_off')
def esp_gpio_off(event):
    pin = validate_pin(event)
    if not pin:
        return
    pin_obj = Pin(pin['number'], pin['mode'])
    pin_obj.value(0)


agent.connect('ws://zentropi.com/{auth}/zentropia')
agent.run()
