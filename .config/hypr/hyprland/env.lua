-------------------------------
---- ENVIRONMENT VARIABLES ----
-------------------------------

-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Environment-variables/

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

-- Wayland support for common toolkits (from s3rius/dotfiles)
hl.env("MOZ_ENABLE_WAYLAND", "1")
hl.env("QT_QPA_PLATFORM", "xcb")
hl.env("QT_QPA_PLATFORMTHEME", "gtk3")
hl.env("TERMINAL", "gnome-terminal")


