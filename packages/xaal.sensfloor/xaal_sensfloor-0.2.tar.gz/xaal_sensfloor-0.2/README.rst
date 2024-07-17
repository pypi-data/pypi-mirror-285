
xaal.sensfloor
==============
This is a gateway for Future Shape Sensfloor to xAAL. It use the websocket API provided by the Sensfloor.

https://future-shape.com/en/system/


WARNINGs
--------
- Sensfloor is only compliant w/ socketio 5.0.0 (won't work on 5.5.*)
- Due to mess in engineio signal handler, the GW is unable to call eng.shutdown()
  => This is enought for me right now, but still be carefull.
  => This bug raise a RuntineError on exit.. but not on console/self.shutdown()
