-- Fallback for unknown PCs and newly connected displays.
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "1",
})

hl.monitor({
    output   = "desc:Najing CEC Panda FPD Technology CO. ltd 0x004D",
    mode     = "1920x1080@144",
    position = "0x0",
    scale    = "1",
})

hl.monitor({
    output   = "desc:LG Electronics 24EA53 310RAHHEJ249",
    mode     = "1920x1080@60",
    position = "1920x0",
    scale    = "1",
})

-- TV over HDMI. Connect it, run `hyprctl monitors all`, then replace the
-- output description and params below. Keep it description-based so it does
-- not conflict with the LG monitor when both use the same HDMI connector.
-- hl.monitor({
--     output   = "desc:YOUR TV DESCRIPTION",
--     mode     = "preferred",
--     position = "1920x0",
--     scale    = "1",
-- })
