#include "7seg.h"

static int display_value = 0;
/* Common-cathode 7-segment patterns for digits 0..9. */
static const uint8_t seg7[10] = {0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F};

void Set7SegDisplayValue(int value)
{
    if (value >= 0 && value <= 99)
    {
        display_value = value;
    }
}

int Get7SegDisplayValue(void)
{
    return display_value;
}

void Run7SegDisplay(void)
{
    int donvi = display_value % 10;

    GPIOE->ODR = (GPIOE->ODR & 0x00FFU) | ((uint16_t)seg7[donvi] << 8);
    HAL_GPIO_WritePin(GPIOG, GPIO_PIN_3, GPIO_PIN_SET);
}
