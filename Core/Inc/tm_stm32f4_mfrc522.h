#ifndef TM_STM32F4_MFRC522_H
#define TM_STM32F4_MFRC522_H

#include "main.h"

#define MI_OK 0U
#define MI_NOTAGERR 1U
#define MI_ERR 2U

#define PICC_REQIDL 0x26U
#define PICC_REQALL 0x52U

void MFRC522_Init(void);
uint8_t MFRC522_Check(uint8_t *id);
uint8_t MFRC522_Request(uint8_t req_mode, uint8_t *tag_type);
uint8_t MFRC522_Anticoll(uint8_t *serial_number);
void MFRC522_Halt(void);
uint8_t MFRC522_ReadRegister(uint8_t address);
void MFRC522_WriteRegister(uint8_t address, uint8_t value);

#endif
