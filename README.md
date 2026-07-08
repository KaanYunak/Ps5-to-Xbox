# DualSense to Xbox Bridge

DualSense / PS5 kolunu Windows'ta sanal Xbox 360 kolu olarak gosteren dusuk gecikmeli bir mapper.

Hedef senaryo: Xbox Game Pass / Microsoft Store oyunlari Steam Input katmani olmadan calistigi icin PS5 kolunu gormeyebilir. Bu uygulama DualSense HID raporlarini okuyup Windows'a XInput uyumlu sanal Xbox 360 controller olarak yollar.

## Mimari

```text
DualSense (USB/Bluetooth HID)
        |
        v
ps5_to_xbox HID reader
        |
        v
DualSense report parser + mapping
        |
        v
vgamepad -> ViGEmBus -> Virtual Xbox 360 Controller
        |
        v
Game Pass / Forza
```

Notlar:

- En dusuk gecikme icin USB kablo tavsiye edilir.
- Bluetooth raporlari icin temel destek var, ama ilk pratik dogrulamayi USB ile yapmak daha saglikli.
- Cift input olursa HidHide ile fiziksel DualSense'i oyundan gizleyip bu uygulamayi whitelist etmek gerekir.
- ViGEmBus projesi artik emekli/arsiv durumunda, ancak `vgamepad` Windows'ta sanal Xbox 360 kolunu bu bus uzerinden olusturur.

## Neden tamamen kendi surucumuz degil?

Bu projede bizim kodumuz olan kisimlar:

- DualSense HID report parser
- PS5 tus/axis -> Xbox tus/axis mapping
- reconnect dongusu
- CLI ve testler

Dis bagimlilik olarak kalan kisimlar:

- `hidapi`: DualSense raporlarini kullanici alanindan okumak icin.
- `vgamepad`: sanal Xbox 360 controller state'ini ViGEmBus'a gondermek icin.
- ViGEmBus: Windows'a sanal Xbox 360 controller gosteren imzali kernel-mode bus driver.

Tamamen kendi sanal Xbox driver'imizi yazmak teknik olarak mumkun, ama pratik MVP degil. Windows'ta virtual driver'lar da fiziksel donanim driver'lariyla ayni kernel-mode imza kurallarina tabi. Public kullanilacak yeni bir kernel-mode driver icin Microsoft imzasi / attestation sureci gerekir. Bu da koddan cok sertifika, driver signing, test mode, kurulum ve anti-cheat uyumlulugu problemi demek.

Daha mantikli yol: once user-mode mapper'i bizim kodumuz olarak saglamlastirmak. Sonraki asamada istersek `hidapi` yerine dogrudan Win32 HID/Raw Input, `vgamepad` yerine de dogrudan ViGEmClient DLL binding yazabiliriz. Ama Windows'a sanal Xbox cihazi gosteren imzali kernel driver ihtiyaci yine kalir.

## Gereksinimler

- Windows 10/11
- Python 3.10+ (`install.cmd` Python yoksa `winget` ile Python 3.12 kurmayi dener)
- DualSense / PS5 kolu
- Python paketleri:

```cmd
install.cmd
```

`vgamepad` kurulumu Windows'ta ViGEmBus surucusunu da kurabilir. Surucu kurulumunda Windows yonetici izni isteyebilir.

Manuel kurulum:

```cmd
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
```

## Kullanim

Kolu USB ile baglayin, sonra:

```cmd
list-devices.cmd
run.cmd
```

Deadzone ayari:

```cmd
run.cmd --deadzone 0.05
```

Debug:

```cmd
run.cmd --verbose
run.cmd --dump-raw
```

Oyunda iki controller gorunurse:

1. HidHide kurun.
2. DualSense cihazini gizleyin.
3. Bu uygulamayi calistiran `python.exe` yolunu HidHide whitelist'e ekleyin.
4. Kolu cikartip yeniden takin.

## Test

Parser testleri dis bagimlilik istemez:

```cmd
test.cmd
```

## Kapsam

Su anki MVP:

- DualSense USB input report parser
- DualSense Bluetooth input report parser icin temel offset destegi
- Face buttons, d-pad, shoulders, triggers, sticks, start/back, thumb buttons, PS tusu mapping
- Sanal Xbox 360 controller cikisi
- Otomatik reconnect dongusu

Sonraki adimlar:

- Gercek cihazdan raw report ornekleriyle Bluetooth offset dogrulamasi
- Rumble geri bildirimi
- Tray app / baslat-durdur UI
- Per-game profil ve deadzone kaydi

## Referanslar

- `vgamepad`: https://pypi.org/project/vgamepad/
- ViGEmBus arsiv / EOL: https://docs.nefarius.at/projects/ViGEm/End-of-Life/
- HidHide setup: https://docs.nefarius.at/projects/HidHide/Simple-Setup-Guide/
- `hidapi`: https://pypi.org/project/hidapi/
- Microsoft kernel-mode driver signing: https://learn.microsoft.com/en-us/windows-hardware/drivers/install/kernel-mode-code-signing-requirements--windows-vista-and-later-
- Microsoft driver code signing requirements: https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-reqs
