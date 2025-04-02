#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/debug.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"
#include "driverlib/uart.h"
#include "driverlib/timer.h"
#include "driverlib/interrupt.h"
#include "driverlib/pin_map.h"
#include "driverlib/systick.h"
#include "utils/uartstdio.c"
#include <string.h>
#include <stdlib.h>
#include "driverlib/pwm.h"

#ifdef DEBUG
void
_error_(char *pcFilename, uint32_t ui32Line)
{
    while(1);
}
#endif
uint32_t FS=120000000*15; //120 MHz
void timer0A_handler(void);
uint8_t switch_state=0;
char  msg[]="h";
char data[100];
char c[100];
uint32_t aux=0;
uint32_t aux2=0;

uint32_t duty=0;
volatile uint32_t flag=10;
volatile uint32_t width=400;

int distancia=0;
uint32_t reloj;

#define TIMEOUT 1000000 
int
main(void)
{
    SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480), 120000000);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, 0x02); // PN2 (trigger) y PN3 (echo)
    GPIOPinWrite(GPIO_PORTF_BASE, 0x02, 0x00); // Apaga PN0 y PN1
  //UART
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);

    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, 0x03);

    UARTStdioConfig(0, 9600, 120000000);
    //PWM
    // Enable the PWM0 peripheral
    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);


    // Configure the PWM function for this pin.
    GPIOPinConfigure(GPIO_PF1_M0PWM1);
    GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_1);

    // wait for the PWM0 module to be ready.
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_PWM0))
    {
    }
    // Configure the PWM generator for count down mode with immediate updates to the parameters.
    PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    // Set the period. For a 50 KHz frequency, the period = 1/50,000, or 20 microseconds.
    // For a 20 MHz clock, this translates to 400 clock ticks. Use this value to set the period.
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, 400);


    // Start the timers in generator 0.
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    // Enable the outputs.
    PWMOutputState(PWM0_BASE, (PWM_OUT_1_BIT), true);    
    while(1)
    {   
            while (UARTCharsAvail(UART0_BASE)) {
                UARTgets(data, 100);
                duty = atoi(data);
            if (duty != 200 && duty != aux2) {
                aux2=duty;
                UARTprintf("%d\n", aux2);  // Confirmar recepción
            }

            }

        GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, GPIO_PIN_1);
        PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, (400*aux2)/100);

        SysCtlDelay((800000)); // ~1 segundo (depende de clock)
    }
}
void timer0A_handler(void)
{
    // Clear timer
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
}