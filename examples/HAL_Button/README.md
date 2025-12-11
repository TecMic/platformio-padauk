# Button Example (HAL)

In this example, the LED lights up for one second every time a button is pressed (falling edge).
It demonstrates the use of GPIO interrupts and the timeout functions. 

### Hardware Circuit
By default, the LED is placed on the PA4 pin with a current sink configuration.\
The button is placed on the PA0 pin. For the PFS154 only PA0 and PB0 support GPIO interrupts. 

### Compatibility
<mark>This example is only tested with the PFS154 microcontroller!

>See [easypdk-hal](https://github.com/TecMic/framework-easypdk-hal) for more info about the HAL lib.