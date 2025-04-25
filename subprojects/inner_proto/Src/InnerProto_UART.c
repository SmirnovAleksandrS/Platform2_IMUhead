#include "InnerProto_UART.h"

uint_least32_t Crc32(unsigned char *buf, size_t len)
{
    uint_least32_t crc_table[256];
    uint_least32_t crc; int i, j;

    for (i = 0; i < 256; i++)
    {
        crc = i;
        for (j = 0; j < 8; j++)
            crc = crc & 1 ? (crc >> 1) ^ 0xEDB88320UL : crc >> 1;

        crc_table[i] = crc;
    };

    crc = 0xFFFFFFFFUL;

    while (len--)
        crc = crc_table[(crc ^ *buf++) & 0xFF] ^ (crc >> 8);

    return crc ^ 0xFFFFFFFFUL;
}

HAL_StatusTypeDef IPUART_sendData(uint8_t length, uint8_t* data, uint8_t type){
    uint8_t buffer[262];    //размер буфера 7e+len+type+255data+4crc
    buffer[0] = START_SEQUENCE;
    buffer[1] = length;
    buffer[2] = type; 
    memcpy(buffer+3, data, length);
    union u32_to_u8 crc;
    crc.u32 = Crc32(data, length);
    memcpy(buffer+3+length, crc.u8, 4);
    return HAL_UART_Transmit(&huart2, buffer, length + 7, HAL_UART_TIMEOUT);
}

HAL_StatusTypeDef IPUART_send3u16(uint16_t x, uint16_t y, uint16_t z, uint8_t type){
    union u16_to_u8 transform;
    uint8_t buffer[6];

    transform.u16 = x;
    memcpy(buffer, transform.u8, 2);
    transform.u16 = y;
    memcpy(buffer + 2, transform.u8, 2);
    transform.u16 = z;
    memcpy(buffer + 4, transform.u8, 2);
    return IPUART_sendData(6, buffer, type);
}