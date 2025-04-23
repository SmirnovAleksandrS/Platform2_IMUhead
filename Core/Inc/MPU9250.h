#ifndef INC_MPU9250_H_
#define INC_MPU9250_H_



#ifdef __cplusplus
extern "C" {
#endif

#include "main.h"
#include "stm32f1xx.h"
#include "math.h"
#include "stdlib.h"
#include "MPU9250RegisterMap.h"

/* I2C Addresses */
#define MPU9250_I2C_ADDR		0xD0
#define MPU9250_I2C_ADDR_MAG	(0x0C << 1)

#define MAG_ST_DRDY_TIMEOUT_MS   100U
/* Structure */
typedef enum {
	MPU9250_RESULT_OK = 0x00,
	MPU9250_RESULT_ERROR,
	MPU9250_RESULT_NC
} MPU9250_Result_t;

typedef enum {
	ACCEL_SCALE_2G = 0x00,
	ACCEL_SCALE_4G = 0x08,
	ACCEL_SCALE_8G = 0x10,
	ACCEL_SCALE_16G = 0x18
} MPU9250_Accel_Scale_t;

typedef enum {
	GYRO_SCALE_250dps = 0x00,
	GYRO_SCALE_500dps = 0x08,
	GYRO_SCALE_1000dps = 0x10,
	GYRO_SCALE_2000dps = 0x18
} MPU9250_Gyro_Scale_t;

typedef enum {
	MAG_SCALE_14bit = 0x00,
	MAG_SCALE_16bit
} MPU9250_Mag_Scale_t;

typedef enum {
	MPU9250_Device_0 = 0x00,
	MPU9250_Device_1 = 0x02
} MPU9250_Device_t;

typedef struct {
    /* полученные данные */
    float   acc[3], gyro[3], mag[3], temp;
    int16_t acc_raw[3], gyro_raw[3], mag_raw[3], temp_raw;
    float   accMult, gyroMult, magMult, tempMult;

    /* I2C-адреса */
    uint8_t I2C_Addr;      /* MPU9250_I2C_ADDR | MPU9250_I2C_ADDR_MAG */
    uint8_t I2C_Addr_Mag;

    /* параметры конфигурации */
    MPU9250_Device_t      DevAddr;
    MPU9250_Accel_Scale_t AccelScale;
    uint8_t               Accel_DLPF;
    MPU9250_Gyro_Scale_t  GyroScale;
    uint8_t               Gyro_DLPF;
    uint8_t               SampleDiv;
    MPU9250_Mag_Scale_t   MagScale;
    uint8_t               MagMode;
} MPU9250_t;

struct test_s {
    unsigned long gyro_sens;
    unsigned long accel_sens;
    unsigned char reg_rate_div;
    unsigned char reg_lpf;
    unsigned char reg_gyro_fsr;
    unsigned char reg_accel_fsr;
    unsigned short wait_ms;
    unsigned char packet_thresh;
    float min_dps;
    float max_dps;
    float max_gyro_var;
    float min_g;
    float max_g;
    float max_accel_var;

    float max_g_offset;
    unsigned short sample_wait_ms;
};

typedef enum { ST_FAIL=0, ST_PASS=1 } ST_Result;

/* Sensor Functions */
MPU9250_Result_t MPU9250_Init(MPU9250_t *MPU9250, MPU9250_Device_t dev, MPU9250_Accel_Scale_t accScale, MPU9250_Gyro_Scale_t gyroScale, MPU9250_Mag_Scale_t magScale);
MPU9250_Result_t MPU9250_ReadAcc(MPU9250_t *MPU9250);
MPU9250_Result_t MPU9250_ReadGyro(MPU9250_t *MPU9250);
MPU9250_Result_t MPU9250_ReadMag(MPU9250_t *MPU9250);
MPU9250_Result_t MPU9250_ReadTemperature(MPU9250_t *MPU9250);
MPU9250_Result_t MPU9250_DataReady(MPU9250_t *MPU9250);
MPU9250_Result_t isMPU9250Ready(I2C_HandleTypeDef *hi2c, uint8_t device_addr);
ST_Result MPU9250_SelfTest(MPU9250_t *M);
ST_Result MPU9250_MagSelfTest(MPU9250_t *M);
HAL_StatusTypeDef whoAmI_Check(MPU9250_t *mpu9250);

/* I2C R/W Functions */
HAL_StatusTypeDef writeByte(I2C_HandleTypeDef *hi2c, uint8_t device_addr, uint8_t register_addr, uint8_t data);
HAL_StatusTypeDef readByte(I2C_HandleTypeDef *hi2c, uint8_t device_addr, uint8_t register_addr, uint8_t *data);
HAL_StatusTypeDef writeMultiBytes(I2C_HandleTypeDef *hi2c, uint8_t device_addr, uint8_t register_addr, uint8_t *data, uint16_t count);
HAL_StatusTypeDef readMultiBytes(I2C_HandleTypeDef *hi2c, uint8_t device_addr, uint8_t register_addr, uint8_t *data, uint16_t count);

#ifdef __cplusplus
}
#endif

#endif /* INC_MPU9250_H_ */
