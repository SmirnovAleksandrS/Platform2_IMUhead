#ifndef _INNERPROTO_UART_
#define _INNERPROTO_UART_

#ifdef __cplusplus
extern "C" {
#endif

#include "stdlib.h"
#include "stm32f1xx.h"
#include <stddef.h>
#include <string.h>
#include <stdint.h>

#define START_SEQUENCE 0x7E
#define HAL_UART_TIMEOUT 10

#define MAG_DATA_TYPE 0xA
#define ACC_DATA_TYPE 0xB
#define GYRO_DATA_TYPE 0xC

extern UART_HandleTypeDef huart2;

union u16_to_u8
{
  uint8_t u8[2];
  uint16_t u16;
};

union u32_to_u8
{
  uint8_t u8[4];
  uint32_t u32;
};

// typedef enum{
//     IP_OK,
//     IP_ERROR,
// }IP_result;


// uint_least32_t Crc32(unsigned char *buf, size_t len);
HAL_StatusTypeDef IPUART_sendData(uint8_t length, uint8_t* data, uint8_t type);       //Отправка  массива данных
HAL_StatusTypeDef IPUART_send3u16(uint16_t x, uint16_t y, uint16_t z, uint8_t type);  //Шаблон отправки пакета данных от 3-х осевого датчика
#ifdef __cplusplus
}
#endif

#endif