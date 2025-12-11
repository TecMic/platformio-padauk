# HAL BlinkLED Example

This example demonstrates just about the simplest thing you can do: it blinks an LED, on for one second, then off for one second, repeatedly.

Note: This example uses a timer based delay function for one second. 

### Hardware Circuit
By default, the LED is placed on the PA4 pin* (Port A, Bit 4) with a current sink configuration.

This means the negative leg (or cathode) of the LED is connected to the digital pin of the IC, and the positive leg (or anode) of the LED is connected through a current limiting resistor to VDD.
- When the digital pin is LOW, current will flow through the LED and it will light up.
- When the digital pin is HIGH, no current will flow and the LED will turn off.

>_*Note: Please consult the pinout for the specific microcontroller package used to identify the correct physical pin._

### Compatibility
==This example is only tested with the PFS154 microcontroller!==

### Build Stats
- Code Size: 166 words (332 bytes)
- RAM usage: 22 bytes + stack
  - 8 bytes system and other HAL variables
  - 2 bytes in the data region for the upTime value
  - 12 bytes in the overlayed area (min reserved size of HAL)

See [easypdk-hal](https://github.com/TecMic/framework-easypdk-hal) for more info about the HAL lib.