/*
  Button interrupt example with HAL lib

  Turns an LED on for one second, then off for one second, repeatedly.
  Uses timer interrupts for the delay function.
*/

#include "hal_util.h"
#include "hal_gpio.h"
#include "hal_sys_timer.h"
#include "hal_interrupt.h"
#include "hal_startup.h"

#include "startup.h"
#include "auto_sysclock.h"


// LED is placed on the PA4 pin (Port A, Bit 4) with a current sink configuration
#define LED_PIN         PA4
// Button is placed on the PA0 pin (Port A, Bit 0) with internal pull-up
#define BUTTON_PIN      PA0

// LED is active low (current sink), so define helpers for better readability below
#define turnLedOn(pin)  GPIO_PA_Write_Low(LED_PIN)
#define turnLedOff(pin) GPIO_PA_Write_High(LED_PIN)


bool interruptFlag;
Timeout_t Timeout;

void INTERRUPT_FUNCTION(void)
{
    if (IT_PA0_Check_Interrupt())
    {
        IT_PA0_Clear_Interrupt();
        interruptFlag = true;
    }
    SYS_TIME_Tick_Handler(); // Clear interrupt and increase millis
}

// Main program
void main(void)
{
    // Initialize hardware
    GPIO_PA_Init_Output(LED_PIN);   // Set LED as output (all pins are input by default)
    turnLedOff();

    GPIO_PA_Init_Input(BUTTON_PIN); // Optional (input by default)
    GPIO_PA_Enable_PullUp(BUTTON_PIN);
    GPIO_PA_Enable_Digital_Input(BUTTON_PIN);   // Without this, only analog input is enabled
    GPIO_PA_IntEdgeDetect(GPIO_PA0_IT_FALLING); // Default is rising/falling
    IT_PA0_Enable_Interrupt();
    IT_PA0_Clear_Interrupt();

    SYS_TIME_Init(); // Initialize timer for interrupt every ~ 1 ms

    IT_Enable_Interrupts();

    // Main processing loop
    while (1)
    {
        if (interruptFlag)
        {
            turnLedOn();
            SYS_TIME_Set_Timeout(&Timeout, 1000);
            interruptFlag = false;
        }

        if (SYS_TIME_Is_Timeout_Set(&Timeout) && SYS_TIME_Check_Timeout(&Timeout))
        {
            turnLedOff();
        }

        // do something else
    }
}

// Startup code - Setup/calibrate system clock
unsigned char STARTUP_FUNCTION(void)
{
    // Initialize the system clock (CLKMD register) with the IHRC, ILRC, or EOSC clock source and correct divider.
    // The AUTO_INIT_SYSCLOCK() macro uses F_CPU (defined in the Makefile) to choose the IHRC or ILRC clock source and divider.
    // Alternatively, replace this with the more specific PDK_SET_SYSCLOCK(...) macro from pdk/sysclock.h
    AUTO_INIT_SYSCLOCK();

    // All registers are in a undefined state at startup, so we clear the important ones
    STARTUP_Set_Registers_Default();
    // STARTUP_Set_Registers_Default_Optional();

    // Insert placeholder code to tell EasyPdkProg to calibrate the IHRC or ILRC internal oscillator.
    // The AUTO_CALIBRATE_SYSCLOCK(...) macro uses F_CPU (defined in the Makefile) to choose the IHRC or ILRC oscillator.
    // Alternatively, replace this with the more specific EASY_PDK_CALIBRATE_IHRC(...) or EASY_PDK_CALIBRATE_ILRC(...) macro from easy-pdk/calibrate.h
    AUTO_CALIBRATE_SYSCLOCK(TARGET_VDD_MV);

    return 0; // Return 0 to inform SDCC to continue with normal initialization.
}
