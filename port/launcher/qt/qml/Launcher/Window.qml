import QtQuick
import QtQuick.Window
import Launcher

Window {
    id: win
    property alias current: main.current
    property alias animate: main.animate
    width: 1120
    height: 700
    minimumWidth: 1000
    minimumHeight: 640
    visible: true
    color: Theme.bg
    title: "The Last of Us Remastered — PC"
    Main { id: main; anchors.fill: parent }
}
