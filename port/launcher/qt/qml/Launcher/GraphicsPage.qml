import QtQuick
import QtQuick.Controls.Basic
import Launcher

Item {
    id: page
    readonly property color accent: Theme.accents.graphics

    ListView {
        id: list
        anchors.fill: parent
        anchors.leftMargin: 36; anchors.rightMargin: 36
        clip: true
        model: Backend.graphicsRows
        spacing: 2
        boundsBehavior: Flickable.StopAtBounds
        delegate: OptionRow { d: modelData; accent: page.accent; onValueSet: (id, value) => Backend.setGraphics(id, value) }
        footer: Column {
            width: list.width
            topPadding: 8; bottomPadding: 24
            Rectangle {
                x: 0; width: list.width; radius: 12; color: Theme.card; border.width: 1; border.color: Theme.cardLine
                height: cacheRow.implicitHeight + 28
                Row {
                    id: cacheRow
                    x: 18; y: 14; width: parent.width - 36; spacing: 14
                    Column {
                        width: parent.width - 160; spacing: 4
                        Text { text: Theme.tr("clear_cache"); color: Theme.text; font.family: Theme.fontText; font.pixelSize: 15; font.weight: Font.DemiBold }
                        Text { visible: Backend.notice !== ""; width: parent.width; text: Backend.notice; wrapMode: Text.WordWrap
                               color: Theme.textDim; font.family: Theme.fontText; font.pixelSize: 13 }
                    }
                    GhostButton { text: Theme.tr("clear_cache"); enabled: Backend.canClear; onClicked: Backend.clearCache() }
                }
            }
        }
        header: Column {
            width: list.width; spacing: 10
            topPadding: 26; bottomPadding: 8
            Text { text: Theme.tr("gfx_title"); color: "#fff"; font.family: Theme.fontDisplay; font.variableAxes: ({ "wght": 800 }); font.pixelSize: 42
                   font.weight: Font.ExtraBold; font.capitalization: Font.AllUppercase; font.letterSpacing: 2.1 }
            Text { width: parent.width; text: Theme.tr("gfx_intro"); wrapMode: Text.WordWrap; color: Theme.textDim
                   font.family: Theme.fontText; font.pixelSize: 13; lineHeight: 1.35; lineHeightMode: Text.ProportionalHeight }
        }
        ScrollBar.vertical: ScrollBar {
            id: bar
            contentItem: Rectangle { implicitWidth: 6; radius: 3; color: bar.pressed ? Theme.ghostLineHover : Theme.ghostLine }
            background: Item { }
        }
    }
}
