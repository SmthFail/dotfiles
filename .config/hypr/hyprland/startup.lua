hl.on("hyprland.start", function()
    hl.exec_cmd("hyprpaper &")
    hl.exec_cmd("waybar -c ~/.config/hypr/waybar/config.jsonc -s ~/.config/hypr/waybar/style.css &")
    hl.exec_cmd("swaync -c ~/.config/hypr/swaync/config.json -s ~/.config/hypr/swaync/style.css &")
end)


