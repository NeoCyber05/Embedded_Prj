#include "tm_stm32f4_mfrc522.h"

#define MFRC522_MAX_LEN 16U

#define MFRC522_REG_COMMAND 0x01U
#define MFRC522_REG_COM_IEN 0x02U
#define MFRC522_REG_DIV_IRQ 0x05U
#define MFRC522_REG_COM_IRQ 0x04U
#define MFRC522_REG_ERROR 0x06U
#define MFRC522_REG_STATUS2 0x08U
#define MFRC522_REG_FIFO_DATA 0x09U
#define MFRC522_REG_FIFO_LEVEL 0x0AU
#define MFRC522_REG_CONTROL 0x0CU
#define MFRC522_REG_BIT_FRAMING 0x0DU
#define MFRC522_REG_COLL 0x0EU
#define MFRC522_REG_MODE 0x11U
#define MFRC522_REG_TX_CONTROL 0x14U
#define MFRC522_REG_TX_ASK 0x15U
#define MFRC522_REG_CRC_RESULT_H 0x21U
#define MFRC522_REG_CRC_RESULT_L 0x22U
#define MFRC522_REG_T_MODE 0x2AU
#define MFRC522_REG_T_PRESCALER 0x2BU
#define MFRC522_REG_T_RELOAD_H 0x2CU
#define MFRC522_REG_T_RELOAD_L 0x2DU

#define PCD_IDLE 0x00U
#define PCD_CALC_CRC 0x03U
#define PCD_TRANSCEIVE 0x0CU
#define PCD_SOFT_RESET 0x0FU

#define PICC_ANTICOLL_CL1 0x93U
#define PICC_HALT 0x50U

static uint8_t MFRC522_ToCard(uint8_t command,
                              uint8_t *send_data,
                              uint8_t send_len,
                              uint8_t *back_data,
                              uint16_t *back_len);
static void MFRC522_AntennaOn(void);
static void MFRC522_ClearBitMask(uint8_t reg, uint8_t mask);
static void MFRC522_CalculateCRC(uint8_t *data, uint8_t length, uint8_t *result);
static void MFRC522_Reset(void);
static void MFRC522_SetBitMask(uint8_t reg, uint8_t mask);
static uint8_t MFRC522_SPITransfer(uint8_t data);

static void MFRC522_Select(void)
{
  HAL_GPIO_WritePin(MFRC522_CS_GPIO_Port, MFRC522_CS_Pin, GPIO_PIN_RESET);
}

static void MFRC522_Deselect(void)
{
  uint32_t timeout = 100000U;

  while (((SPI4->SR & SPI_SR_BSY) != 0U) && (timeout > 0U))
  {
    timeout--;
  }

  HAL_GPIO_WritePin(MFRC522_CS_GPIO_Port, MFRC522_CS_Pin, GPIO_PIN_SET);
}

static uint8_t MFRC522_SPITransfer(uint8_t data)
{
  uint32_t timeout = 100000U;

  while (((SPI4->SR & SPI_SR_TXE) == 0U) && (timeout > 0U))
  {
    timeout--;
  }

  if (timeout == 0U)
  {
    return 0U;
  }

  *(__IO uint8_t *)&SPI4->DR = data;

  timeout = 100000U;
  while (((SPI4->SR & SPI_SR_RXNE) == 0U) && (timeout > 0U))
  {
    timeout--;
  }

  if (timeout == 0U)
  {
    return 0U;
  }

  return *(__IO uint8_t *)&SPI4->DR;
}

void MFRC522_WriteRegister(uint8_t address, uint8_t value)
{
  MFRC522_Select();
  MFRC522_SPITransfer((address << 1U) & 0x7EU);
  MFRC522_SPITransfer(value);
  MFRC522_Deselect();
}

uint8_t MFRC522_ReadRegister(uint8_t address)
{
  uint8_t value;

  MFRC522_Select();
  MFRC522_SPITransfer(((address << 1U) & 0x7EU) | 0x80U);
  value = MFRC522_SPITransfer(0x00U);
  MFRC522_Deselect();

  return value;
}

static void MFRC522_SetBitMask(uint8_t reg, uint8_t mask)
{
  uint8_t tmp = MFRC522_ReadRegister(reg);
  MFRC522_WriteRegister(reg, tmp | mask);
}

static void MFRC522_ClearBitMask(uint8_t reg, uint8_t mask)
{
  uint8_t tmp = MFRC522_ReadRegister(reg);
  MFRC522_WriteRegister(reg, tmp & (uint8_t)(~mask));
}

static void MFRC522_Reset(void)
{
  MFRC522_WriteRegister(MFRC522_REG_COMMAND, PCD_SOFT_RESET);
  HAL_Delay(50);
}

static void MFRC522_AntennaOn(void)
{
  uint8_t temp = MFRC522_ReadRegister(MFRC522_REG_TX_CONTROL);

  if ((temp & 0x03U) != 0x03U)
  {
    MFRC522_SetBitMask(MFRC522_REG_TX_CONTROL, 0x03U);
  }
}

void MFRC522_Init(void)
{
  HAL_GPIO_WritePin(MFRC522_RST_GPIO_Port, MFRC522_RST_Pin, GPIO_PIN_RESET);
  HAL_Delay(20);
  HAL_GPIO_WritePin(MFRC522_RST_GPIO_Port, MFRC522_RST_Pin, GPIO_PIN_SET);
  HAL_Delay(50);

  MFRC522_Reset();

  MFRC522_WriteRegister(MFRC522_REG_T_MODE, 0x8DU);
  MFRC522_WriteRegister(MFRC522_REG_T_PRESCALER, 0x3EU);
  MFRC522_WriteRegister(MFRC522_REG_T_RELOAD_L, 30U);
  MFRC522_WriteRegister(MFRC522_REG_T_RELOAD_H, 0U);
  MFRC522_WriteRegister(MFRC522_REG_TX_ASK, 0x40U);
  MFRC522_WriteRegister(MFRC522_REG_MODE, 0x3DU);

  MFRC522_AntennaOn();
}

uint8_t MFRC522_Request(uint8_t req_mode, uint8_t *tag_type)
{
  uint16_t back_bits = 0U;
  uint8_t status;

  MFRC522_WriteRegister(MFRC522_REG_BIT_FRAMING, 0x07U);

  tag_type[0] = req_mode;
  status = MFRC522_ToCard(PCD_TRANSCEIVE, tag_type, 1U, tag_type, &back_bits);

  if ((status != MI_OK) || (back_bits != 0x10U))
  {
    status = MI_ERR;
  }

  return status;
}

uint8_t MFRC522_Anticoll(uint8_t *serial_number)
{
  uint8_t status;
  uint8_t check = 0U;
  uint8_t i;
  uint16_t un_len = 0U;

  MFRC522_ClearBitMask(MFRC522_REG_STATUS2, 0x08U);
  MFRC522_WriteRegister(MFRC522_REG_BIT_FRAMING, 0x00U);
  MFRC522_ClearBitMask(MFRC522_REG_COLL, 0x80U);

  serial_number[0] = PICC_ANTICOLL_CL1;
  serial_number[1] = 0x20U;

  status = MFRC522_ToCard(PCD_TRANSCEIVE, serial_number, 2U,
                          serial_number, &un_len);

  if (status == MI_OK)
  {
    for (i = 0U; i < 4U; i++)
    {
      check ^= serial_number[i];
    }

    if (check != serial_number[4])
    {
      status = MI_ERR;
    }
  }

  return status;
}

uint8_t MFRC522_Check(uint8_t *id)
{
  uint8_t status;
  uint8_t tag_type[2];

  status = MFRC522_Request(PICC_REQIDL, tag_type);
  if (status == MI_OK)
  {
    status = MFRC522_Anticoll(id);
  }

  return status;
}

void MFRC522_Halt(void)
{
  uint8_t buffer[4];
  uint16_t un_len = 0U;

  buffer[0] = PICC_HALT;
  buffer[1] = 0U;
  MFRC522_CalculateCRC(buffer, 2U, &buffer[2]);

  (void)MFRC522_ToCard(PCD_TRANSCEIVE, buffer, 4U, buffer, &un_len);
}

static void MFRC522_CalculateCRC(uint8_t *data, uint8_t length, uint8_t *result)
{
  uint8_t i;
  uint8_t n;
  uint32_t timeout = 0xFFU;

  MFRC522_ClearBitMask(MFRC522_REG_DIV_IRQ, 0x04U);
  MFRC522_SetBitMask(MFRC522_REG_FIFO_LEVEL, 0x80U);

  for (i = 0U; i < length; i++)
  {
    MFRC522_WriteRegister(MFRC522_REG_FIFO_DATA, data[i]);
  }

  MFRC522_WriteRegister(MFRC522_REG_COMMAND, PCD_CALC_CRC);

  do
  {
    n = MFRC522_ReadRegister(MFRC522_REG_DIV_IRQ);
    timeout--;
  } while ((timeout != 0U) && ((n & 0x04U) == 0U));

  result[0] = MFRC522_ReadRegister(MFRC522_REG_CRC_RESULT_L);
  result[1] = MFRC522_ReadRegister(MFRC522_REG_CRC_RESULT_H);
}

static uint8_t MFRC522_ToCard(uint8_t command,
                              uint8_t *send_data,
                              uint8_t send_len,
                              uint8_t *back_data,
                              uint16_t *back_len)
{
  uint8_t status = MI_ERR;
  uint8_t irq_en = 0U;
  uint8_t wait_irq = 0U;
  uint8_t last_bits;
  uint8_t n;
  uint8_t i;
  uint32_t timeout = 2000U;

  if (command == PCD_TRANSCEIVE)
  {
    irq_en = 0x77U;
    wait_irq = 0x30U;
  }

  MFRC522_WriteRegister(MFRC522_REG_COM_IEN, irq_en | 0x80U);
  MFRC522_ClearBitMask(MFRC522_REG_COM_IRQ, 0x80U);
  MFRC522_SetBitMask(MFRC522_REG_FIFO_LEVEL, 0x80U);
  MFRC522_WriteRegister(MFRC522_REG_COMMAND, PCD_IDLE);

  for (i = 0U; i < send_len; i++)
  {
    MFRC522_WriteRegister(MFRC522_REG_FIFO_DATA, send_data[i]);
  }

  MFRC522_WriteRegister(MFRC522_REG_COMMAND, command);

  if (command == PCD_TRANSCEIVE)
  {
    MFRC522_SetBitMask(MFRC522_REG_BIT_FRAMING, 0x80U);
  }

  do
  {
    n = MFRC522_ReadRegister(MFRC522_REG_COM_IRQ);
    timeout--;
  } while ((timeout != 0U) && ((n & 0x01U) == 0U) && ((n & wait_irq) == 0U));

  MFRC522_ClearBitMask(MFRC522_REG_BIT_FRAMING, 0x80U);

  if (timeout != 0U)
  {
    if ((MFRC522_ReadRegister(MFRC522_REG_ERROR) & 0x1BU) == 0U)
    {
      status = MI_OK;

      if ((n & irq_en & 0x01U) != 0U)
      {
        status = MI_NOTAGERR;
      }

      if (command == PCD_TRANSCEIVE)
      {
        n = MFRC522_ReadRegister(MFRC522_REG_FIFO_LEVEL);
        last_bits = MFRC522_ReadRegister(MFRC522_REG_CONTROL) & 0x07U;

        if (last_bits != 0U)
        {
          *back_len = (uint16_t)((uint16_t)(n - 1U) * 8U + last_bits);
        }
        else
        {
          *back_len = (uint16_t)n * 8U;
        }

        if (n == 0U)
        {
          n = 1U;
        }

        if (n > MFRC522_MAX_LEN)
        {
          n = MFRC522_MAX_LEN;
        }

        for (i = 0U; i < n; i++)
        {
          back_data[i] = MFRC522_ReadRegister(MFRC522_REG_FIFO_DATA);
        }
      }
    }
  }

  return status;
}
