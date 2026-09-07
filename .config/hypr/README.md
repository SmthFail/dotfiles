# Hyprland-сессия: что нужно, чтобы это поднялось

Конфиг на Lua: `hyprland.lua` + `hyprland/*.lua`, отдельного `hyprland.conf` нет.

## Пакеты, без которых сессия не собирается

- `hyprland`, `hyprpaper`, `waybar`, `swaync`, `hypridle`, `hyprlock`, `hyprsunset`.
  Юниты их старта приходят **из самих пакетов**
  (`/etc/systemd/user/graphical-session.target.wants/`). Нет пакета — нет юнита, сессия
  стартует пустой (ни бара, ни локскрина, ни таймеров), а `hyprland-session.service` при
  этом «успешен» и вообще не сигнализирует о проблеме. Проверка:
  `systemctl --user list-dependencies graphical-session.target`
- `rofi` (лончер по `SUPER`), `wlogout` (power-меню), `grim` + `slurp` (скриншоты),
  `playerctl` (медиа-клавиши), `brightnessctl` (яркость), `wireplumber`/`pipewire` (`wpctl`),
  `network-manager-gnome` (`nm-connection-editor`), `pavucontrol`, `bluez` (`bluetoothctl`),
  `gnome-terminal` (переменная `TERMINAL`)
- шрифт `JetBrainsMono Nerd Font` — его требует `~/.config/rofi/config.rasi`. Ставится в
  `~/.local/share/fonts/`; без него вместо иконок в меню квадраты.

## Что где лежит

- `~/.config/hypr/` — конфиг Hyprland, `hypridle.conf`, `hyprlock.conf`, `hyprpaper.conf`,
  `waybar/`, `swaync/`, `scripts/` (скриншоты, список биндов), `colors.css`
- `~/.config/rofi/config.rasi` — лончер
- `~/.config/wlogout/` — power-меню. Иконки берутся из `/usr/share/wlogout/icons`, и каждой
  кнопке обязательно собственное правило `#label` в `style.css`, иначе кнопка рисуется пустой
- `~/.config/systemd/user/` — `hyprland-session.service` (поднимает
  `graphical-session.target`, который нельзя стартовать напрямую: `RefuseManualStart=yes`),
  drop-in'и `waybar`/`swaync` с нестандартными путями конфигов, `hyprsunset.service` —
  симлинк на `/dev/null` (штатный mask, класть до `systemctl --user daemon-reload`)
- `~/.config/autostart/org.gnome.SettingsDaemon.Power.desktop` — `Hidden=true`, иначе
  gsd-power прилетает из GNOME и борется за яркость и DPMS
- `SLEEP.md` — блокировка, сон, гибернация: пользовательская часть, правки в `/etc`,
  команды проверки и откат

## Внешности, которых нет в репозитории

- Обои: `hyprpaper.conf` указывает на PNG вне репозитория. Если файла нет — обоев просто не
  будет, на бинды, бар, локскрин и сон это не влияет: hyprpaper на неразрешённом пути только
  пишет `ERR` в `journalctl --user-unit=hyprpaper` и не выходит (проверено на конфиге с
  заведомо несуществующим файлом).
- `mimeapps.list`, `dconf`, gtk-темы намеренно не хранятся — это состояние конкретной машины
  (темы и так стоковые Ubuntu: `Yaru-dark`, `Cantarell`).

## Как обновлять из репозитория

Репозиторий голый (`core.bare=true`), рабочее дерево — `$HOME`, поэтому только с флагами:

    git --git-dir=$HOME/work/git/dotfiles --work-tree=$HOME status -- .config
    git --git-dir=$HOME/work/git/dotfiles --work-tree=$HOME diff -- .config/hypr

`checkout --` затирает локальные правки без вопроса, поэтому сначала `diff`. Файлы добавлять
исключительно явными путями: в `~/.config/systemd/user/` лежат snap-симлинки из `*.wants/`,
а в `~/.config/hypr/scripts/` — `__pycache__` (правило в `.gitignore` на него не действует,
путь там указан без точки).
