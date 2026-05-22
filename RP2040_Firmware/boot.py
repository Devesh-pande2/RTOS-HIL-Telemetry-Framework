import usb_cdc

# Enable both the standard console port and the secondary data port
usb_cdc.enable(console=True, data=True)