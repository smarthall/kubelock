import os
import signal

from pathlib import Path

from pydbus import SystemBus
from gi.repository import GLib

loop = GLib.MainLoop()

LOCK_BUS = "org.freedesktop.login1"
SEAT_OBJ = ""

def cli():
    bus = SystemBus()
    obj = bus.get(LOCK_BUS)

    # Find the current session
    seat = bus.get(LOCK_BUS, obj.GetSeat("auto"))
    session = bus.get(LOCK_BUS, seat.ActiveSession[1])
    assert(session.Active)

    # Subscribe to property changes
    session.PropertiesChanged.connect(property_handler)

    # Start the main loop
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass

def property_handler(interface_name, changed_properties, invalidated_properties):
    # Is it a property we are interested in?
    if 'LockedHint' not in changed_properties:
        return

    # Did we lock the screen?
    locked_hint = changed_properties['LockedHint']
    if locked_hint == False:
        return

    # Remove the kubeconfig file
    kubeconfig = Path.home() / ".kube" / "config"
    if os.path.exists(kubeconfig):
        os.remove(kubeconfig)

def signal_handler(sig, frame):
    if sig == signal.SIGTERM and loop.is_running():
        loop.quit()
