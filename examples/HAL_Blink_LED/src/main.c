/*
  BlinkLED with HAL lib

  Turns an LED on for one second, then off for one second, repeatedly.
  Uses timer interrupts for the delay function.
*/

#include "hal_util.h"
#include "hal_gpio.h"
#include "hal_sys_timer.h"

#include "startup.h"
#include "auto_sysclock.h"


// LED is placed on the PA4 pin (Port A, Bit 4) with a current sink configuration
#define LED_PIN         PA4

// LED is active low (current sink), so define helpers for better readability below
#define turnLedOn(pin)  GPIO_PA_Write_Low(PA4)
#define turnLedOff(pin) GPIO_PA_Write_High(PA4)

void INTERRUPT_FUNCTION(void)
{
    SYS_TIME_Tick_Handler(); // Clear interrupt and increase millis up
}

// Main program
void main(void)
{
    // Initialize hardware
    GPIO_PA_Init_Output(LED_PIN) // Set LED as output (all pins are input by default)
    turnLedOff(LED_PIN);

    SYS_TIME_Init(); // Initialize timer for interrupt every ~ 1 ms

    // Main processing loop
    while (1)
    {
        turnLedOn(LED_PIN);
        Delay_ms(1000);
        turnLedOff(LED_PIN);
        Delay_ms(1000);
    }
}

// Startup code - Setup/calibrate system clock
unsigned char STARTUP_FUNCTION(void)
{
    // Initialize the system clock (CLKMD register) with the IHRC, ILRC, or EOSC clock source and correct divider.
    // The AUTO_INIT_SYSCLOCK() macro uses F_CPU (defined in the Makefile) to choose the IHRC or ILRC clock source and divider.
    // Alternatively, replace this with the more specific PDK_SET_SYSCLOCK(...) macro from pdk/sysclock.h
    AUTO_INIT_SYSCLOCK();

    // Insert placeholder code to tell EasyPdkProg to calibrate the IHRC or ILRC internal oscillator.
    // The AUTO_CALIBRATE_SYSCLOCK(...) macro uses F_CPU (defined in the Makefile) to choose the IHRC or ILRC oscillator.
    // Alternatively, replace this with the more specific EASY_PDK_CALIBRATE_IHRC(...) or EASY_PDK_CALIBRATE_ILRC(...) macro from easy-pdk/calibrate.h
    AUTO_CALIBRATE_SYSCLOCK(TARGET_VDD_MV);

    return 0; // Return 0 to inform SDCC to continue with normal initialization.
}
