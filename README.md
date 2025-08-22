# Головной проект сенсорной головы Платформы 2.0
## Сборка проекта

Для сборки проекта достаточно запустить два скрипта:
```bash
./configure.py
```
Он подтянет с гита все используемые библиотеки.
Второй скрипт:
```bash
./build.py
```
Запускает непосредственно сборку проекта.

## Редактирование адресов используемых библиотек

Все используемые либы подгружаются из файла `submodules_list.json`. Содержимое выглядит примерно так:
```json
{
  "libs": {
    "inner_proto": {
      "name": "INNER_PROTO",
      "url": "https://github.com/SmirnovAleksandrS/Platform2_InnerProto",
      "rev": "main",
      "dst": "submodules/inner-proto"
    },
    "mpu9250_lib": {
      "name": "MPU9250_LIB",
      "url": "https://github.com/SmirnovAleksandrS/Platform2_MPU9250.git",
      "rev": "main",
      "dst": "submodules/mpu9250-lib"
    },
    "qmc5883_lib": {
      "name": "QMC5883_LIB",
      "url": "https://github.com/SmirnovAleksandrS/Platform2_QMC5883",
      "rev": "main",
      "dst": "submodules/qmc5883-lib"
    }
  }
}

```
"name" это название либы в системе сборки, оно должно совпадать с именем либы в файле export.mk.
"url" это адрес либы в гите, либо абсолютный путь до библиотеки на компьютере, если ее удобнее отлаживать и создавать локально.
"rev" это тег или ветка используемого релиза библиотеки, рекомендуется ставить конкретный тег.
"dst" это адрес куда будет качаться либа. Не рекомендуется переносить ее из папки submodules.
