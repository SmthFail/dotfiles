hl.on("hyprland.start", function()
    -- hyprpaper / waybar / swaync / hypridle / hyprsunset стартуют user-юнитами
    -- (WantedBy=graphical-session.target, включены пакетом в /etc/systemd/user).
    -- Hyprland из GDM этот target не поднимает, поэтому поднимаем его вручную.
    -- Порядок важен: сначала отдаём переменные окружения в user manager
    -- (юниты стоят на ConditionEnvironment=WAYLAND_DISPLAY), потом стартуем target.
    -- Кастомные пути конфигов waybar/swaync заданы drop-in'ами в
    -- ~/.config/systemd/user/<unit>.service.d/override.conf
    hl.exec_cmd("sh -c 'dbus-update-activation-environment --systemd --all; " ..
                "systemctl --user import-environment WAYLAND_DISPLAY DISPLAY XDG_CURRENT_DESKTOP HYPRLAND_INSTANCE_SIGNATURE; " ..
                "systemctl --user start hyprland-session.service'")
end)
