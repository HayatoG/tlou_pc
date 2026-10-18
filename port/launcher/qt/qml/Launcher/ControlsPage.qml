import QtQuick
import QtQuick.Controls.Basic
import Launcher

Item {
    id: page
    readonly property color accent: Theme.accents.controls

    ListView {
        id: list
        anchors.fill: parent
        anchors.leftMargin: 36; anchors.rightMargin: 36
        clip: true
        model: Backend.controlsRows
        spacing: 2
        boundsBehavior: Flickable.StopAtBounds
        delegate: OptionRow { d: modelData; accent: page.accent; onValueSet: (id, value) => Backend.setControls(id, value) }
        header: Column {
            width: list.width; spacing: 10
            topPadding: 26; bottomPadding: 8
            Text { text: Theme.tr("ctl_title"); color: "#fff"; font.family: Theme.fontDisplay; font.variableAxes: ({ "wght": 800 }); font.pixelSize: 42
                   font.weight: Font.ExtraBold; font.capitalization: Font.AllUppercase; font.letterSpacing: 2.1 }
            Text { width: parent.width; text: Theme.tr("ctl_intro"); wrapMode: Text.WordWrap; color: Theme.textDim
                   font.family: Theme.fontText; font.pixelSize: 13; lineHeight: 1.35; lineHeightMode: Text.ProportionalHeight }
        }
        footer: Item { width: 1; height: 24 }
        ScrollBar.vertical: ScrollBar {
            id: bar
            contentItem: Rectangle { implicitWidth: 6; radius: 3; color: bar.pressed ? Theme.ghostLineHover : Theme.ghostLine }
            background: Item { }
        }
    }
}
