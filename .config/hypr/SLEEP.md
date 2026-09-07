# Сон, блокировка, гибернация — что было сломано и как воспроизведено

Состояние на 2026-09-07. Ubuntu 24.04, Hyprland 0.56.2 (конфиг на Lua), hyprlock 0.9.6,
hypridle 0.1.8, ядро 7.0.0-28, NVIDIA 595.84 (open) RTX 3060 Laptop + amdgpu iGPU,
Wi-Fi mt7921e, dual-boot с Windows.

Исходно: локскрин не поднимался вообще, `systemctl suspend` вешал машину намертво,
часы после ребута врали на +3 ч, гибернация была невозможна, кнопка Hibernate в
power-меню вела в никуда.

## Симптом → причина → решение

| Симптом | Причина | Решение |
|---|---|---|
| `SUPER+L`/кнопка Lock: ничего не происходит | `hyprlock` без конфига печатал `No config file at "{}"` и умирал; у Hyprland оставался «crashed lockscreen» | минимальный `hyprlock.conf`; все точки залокa через `loginctl lock-session` |
| Мониторы не гасли и не включались, сон по таймеру не наступал | `hypridle` не был запущен; в Lua-конфиге текстовые диспетчеры не работают | запуск user-юнитами через `graphical-session.target`; диспетчер только как `hl.dsp.dpms({...})` |
| Suspend вешал систему, экран на VT 63, машина не отвечала | `NVreg_PreserveVideoMemoryAllocations=1`: `nv_pmops_suspend` → `-5`, `nvidia-sleep.sh` делал `chvt 63` и падал на RPC к GSP (`rpcRecvPoll 0x62`) | сохранение VRAM выключено + замаскированы `nvidia-suspend/resume/hibernate` |
| Время после загрузки +3 ч, затем `Time jumped backwards` | в RTC лежало локальное время, а Linux считал его UTC (вторая ОС — Windows) | RTC в LOCAL: `timedatectl set-local-rtc 1` (Windows и реестр не трогать) |
| `systemctl hibernate` = swap 4 GiB при RAM 14 GiB, `resume` не задан | гибернация не настраивалась никогда | swap-файл 16 GiB, `resume=`/`resume_offset=` в GRUB, `/sys/power/image_size` зафиксирован |
| Wi-Fi не возвращался из сна | `mt7921e` не резюмируется из ASPM: `pci_pm_resume returns -110` | `disable_aspm=1` таймаут не убрал, но драйвер сам пересоздаёт интерфейс за ~4 с — оставлено как есть |

## Уровень пользователя (в этом репозитории)

- `hypridle.conf` — 3 правила: 600 с залок → 1200 с гашение мониторов → 1800 с сон.
  `lock_cmd = pidof hyprlock || hyprlock` — гард от дублей. `before_sleep_cmd =
  loginctl lock-session`, `after_sleep_cmd`/`unlock_cmd` включают DPMS.
  Проверка: `journalctl --user-unit=hypridle -n 20` → `found 3 rules`.
- `hyprlock.conf` — однотонный фон, `$USER`, `$LAYOUT[en,ru]` с переключением по клику,
  `input-field`. Без скриншота-бэкграунда и blur.
- `hyprland.lua` — `misc.key_press_enables_dpms` / `mouse_move_enables_dpms`, иначе
  погашенный по idle монитор не включается ни клавиатурой, ни мышью.
- `hyprland/startup.lua` — вместо `exec_cmd` на каждый демон один бутстрап сессии:
  `dbus-update-activation-environment --systemd --all`, `systemctl --user
  import-environment …`, `systemctl --user start hyprland-session.service`.
- `hyprland/keybinds.lua` — `SUPER+CTRL+L` → `loginctl lock-session`,
  `SUPER+CTRL+S` → `systemctl suspend`.
- `waybar/config.jsonc` — средняя кнопка иконки питания тоже `loginctl lock-session`
  (раньше дергал `hyprlock` напрямую, отчего и рождался зависший залок).
- `systemd/user/hyprland-session.service` — `graphical-session.target` помечен
  `RefuseManualStart=yes` и не поднимается напрямую; этот юнит тянет его как чужую
  зависимость, а за ним стартуют hypridle/waybar/swaync/hyprpaper (их включает пакет
  через `/etc/systemd/user/graphical-session.target.wants`). `RemainAfterExit=yes`
  обязателен из-за `StopWhenUnneeded=yes` у target.
- `systemd/user/{waybar,swaync}.service.d/override.conf` — конфиги лежат в
  `~/.config/hypr/…`, а не в дефолтных путях; заодно починен `ExecReload` у swaync.
- `systemd/user/hyprsunset.service` — симлинк на `/dev/null`, то есть штатный `mask`
  (hyprsunset конфликтовал с DPMS). При восстановлении репозитория положить файл до
  `systemctl --user daemon-reload`.
- `autostart/org.gnome.SettingsDaemon.Power.desktop` с `Hidden=true` — gsd-power из
  GNOME прилетал в сессию и боролся за яркость/DPMS.
- `wlogout/layout` + `wlogout/style.css` — 6 кнопок: Lock, Logout, Suspend, Hibernate,
  Power Off, Restart. Hibernate: `loginctl lock-session && sleep 2 && systemctl
  hibernate` (клавиша `h`). Иконки заданы правилом на каждый `#label`, поэтому для
  новой кнопки нужен и `#hibernate` в CSS, иначе кнопка рисуется пустой.

## Уровень root (вне репозитория — воспроизводится вручную)

1. NVIDIA, сохранение VRAM выключить:
   `/etc/modprobe.d/nvidia-graphics-drivers-kms.conf` и `/etc/modprobe.d/nvidia.conf`
   ```
   options nvidia NVreg_PreserveVideoMemoryAllocations=0
   options nvidia NVreg_TemporaryFilePath=/var/tmp/nvidia-suspend.bin
   ```
   Заодно замаскировать юниты, которые уводят экран на VT 63:
   `systemctl mask nvidia-suspend.service nvidia-resume.service nvidia-hibernate.service`
2. Wi-Fi: `/etc/modprobe.d/99-mt7921e-suspend.conf` →
   `options mt7921e disable_aspm=1`
3. Часы: `timedatectl set-local-rtc 1` (проверка: `timedatectl show -p LocalRTC`,
   `/etc/adjtime` = `LOCAL`).
4. Гибернация: swap-файл 16 GiB (`/swap.img`, больше, чем RAM 14 GiB), в
   `GRUB_CMDLINE_LINUX_DEFAULT` добавить `resume=UUID=<uuid корня>` и
   `resume_offset=<N>`, где N — первый физический-extent-блок файла подкачки:
   `filefrag -v /swap.img | awk '/^0:/{print $4+0}'`. Плюс
   `/etc/initramfs-tools/conf.d/resume` → `RESUME=/dev/disk/by-uuid/<uuid>`,
   `update-initramfs -u`, `update-grub`.
   Образ сна фиксировать: `/etc/tmpfiles.d/hypr-sleep.conf` →
   `w /sys/power/image_size - - - - 17179869184` (16 GiB), иначе ядро урезает его
   до ~2/5 RAM и гибернация не влезает.
5. **После любой правки параметров nvidia — обязательно `sudo update-initramfs -u` и
   перезагрузка.** `nvidia nvidia_modeset nvidia_uvm nvidia_drm` перечислены в
   `/etc/initramfs-tools/modules`, то есть грузятся на раннем этапе из initramfs,
   а внутри него лежит старая копия `/etc/modprobe.d`. Без пересборки получается
   «в файлах 0, а в ядре 1» — именно на этом мы и попались.

Все `resume_offset`/UUID привязаны к этому диску; на другой машине считать заново.

## Как проверить

```
grep -i PreserveVideoMemory /proc/driver/nvidia/params   # 0
systemctl is-enabled nvidia-suspend.service               # masked
cat /sys/power/resume                                     # не 0:0 (на этой машине 259:6)
grep -o 'resume[^ ]*' /proc/cmdline                        # resume= и resume_offset=
timedatectl show -p LocalRTC                               # LocalRTC=yes
journalctl -k -b 0 | grep -E 'PM: suspend entry|suspend exit'   # оба входа и выхода
journalctl -k -b 0 | grep -cE 'rpcRecvPoll|returns -5|Some devices failed'   # 0
systemctl is-system-running                                # running
```

## Известный шум, который не является поломкой

- `mt7921e … pci_pm_resume returns -110` — сеть живёт через ~4 с после пробуждения,
  `nmcli device status` показывает `connected`.
- `integrity: Problem loading X.509 certificate -65`, `could not find module by
  name='off'`, сообщения `bluetoothd` про SAP, ассерт `gdm3: on_display_added`.

## Откат и восстановление залокa

- Бэкапы всего затронутого: `~/.backup/hypr-sleep-20260907/` (в `root/` — оригиналы
  `/etc/modprobe.d/*`, `/etc/default/grub`, там же записан исходный `resume_offset`).
- Вернуть сохранение VRAM имеет смысл только вместе с `NVreg_DynamicPowerManagement=0x00`,
  `systemctl unmask nvidia-suspend nvidia-resume nvidia-hibernate` и тестом сна:
  на этой прошивке GSP RPC стабильно не поднимается, поэтому оставлено выключенным.
- Если залок «завис» (экран есть, hyprlock не отрисовался): НЕ убивать hyprlock —
  Hyprland останется в crashed lockscreen. Спасает
  `hyprctl eval 'hl.clear_crashed_lockscreen()'` (функция сама отказывается, когда
  сессия не залочена). Из TTY предварительно:
  `export XDG_RUNTIME_DIR=/run/user/1000 HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr | head -1)`.
- Если suspend завис при тесте: `Ctrl+Alt+F3` → логин → `systemctl cancel suspend.target
  sleep.target systemd-suspend.service` → `chvt 2`.
