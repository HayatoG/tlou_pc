pragma Singleton
import QtQuick
import Launcher

// Every color, size and font of the launcher lives here (single source for the visual identity).
// TLOU's own palette: a quarantine-zone amber lamp against near-black, moss green for the
// cordyceps growing back over the city, rust red for danger/infected - distinct from the
// other ports, not matched to them.
QtObject {
    // surfaces
    readonly property color bg: "#0e0f0b"
    readonly property color rail: "#0b0c09"
    readonly property color railLine: "#1c1e16"
    readonly property color navHover: "#171911"
    readonly property color navOn: "#1a1c13"
    readonly property color navOnLine: "#2b2e1f"
    readonly property color card: "#14160f"
    readonly property color cardLine: "#262a1c"
    readonly property color chip: "#16180f"
    readonly property color chipLine: "#292d1e"
    readonly property color ghost: "#171911"
    readonly property color ghostHover: "#1f2217"
    readonly property color ghostLine: "#2d3121"
    readonly property color ghostLineHover: "#444a30"
    // text
    readonly property color text: "#e8e4d8"
    readonly property color textSoft: "#c7c2b0"
    readonly property color textChip: "#d6d1c0"
    readonly property color textMuted: "#a2a08c"
    readonly property color textDim: "#8d8b78"
    readonly property color textFaint: "#7a7868"
    // states
    readonly property color ok: "#6fae4a"     // cordyceps, healthy
    readonly property color warn: "#c9a227"   // the lamp
    readonly property color bad: "#b5452c"    // infected
    readonly property color off: "#5a5a4a"
    // one accent per section
    readonly property color smoke: "#c9a227"  // Play
    readonly property color video: "#6b8f6b"  // Graphics
    readonly property color neon: "#8a7a5b"   // Controls
    readonly property var accents: ({ play: "#c9a227", graphics: "#6b8f6b", controls: "#8a7a5b", mods: "#b5452c" })
    // type
    property string fontDisplay: Backend.fontDisplay
    property string fontText: Backend.fontText
    readonly property int railWidth: 236
    readonly property int heroHeight: 320
    // line icons, 24x24 viewBox (circles written as arcs)
    readonly property var icons: ({
        play: "M7 4.5v15l12-7.5z",
        graphics: "M4 7h10M18 7h2M4 17h2M10 17h10 M18 7a2 2 0 1 0-4 0a2 2 0 1 0 4 0 M10 17a2 2 0 1 0-4 0a2 2 0 1 0 4 0",
        controls: "M7 8h10a4 4 0 0 1 4 4l-1 5a2 2 0 0 1-3.4 1L15 16H9l-1.6 2A2 2 0 0 1 4 17l-1-5a4 4 0 0 1 4-4z",
        mods: "M6 9h12a3 3 0 0 1 0 6H6a3 3 0 0 1 0-6z M17.2 12a2.2 2.2 0 1 0-4.4 0a2.2 2.2 0 1 0 4.4 0"
    })

    // Translation: reading Backend.lang inside makes every binding that calls it re-evaluate
    // when the player switches language.
    function tr(key) { var l = Backend.lang; return Backend.t(key) }
}
