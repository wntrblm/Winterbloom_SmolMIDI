# Winterbloom SmolMIDI

This is a [CircuitPython](https://circuitpython.org) helper library for communicating over MIDI. This library is intentionally minimal and low-level. It's just enough to make using the [`PortIn`](https://circuitpython.readthedocs.io/en/latest/shared-bindings/usb_midi/PortIn.html) bearable. If you are looking for a high-level, beginner-friendly MIDI library please look at [Adafruit CircuitPython MIDI](https://github.com/adafruit/Adafruit_CircuitPython_MIDI).

## Usage

Create a `MidiIn` instance using a `PortIn` instance:

```python
import usb_midi
import winterbloom_smolmidi as smolmidi

midi_in = smolmidi.MidiIn(usb_midi.ports[0])
```

Then use `receive` to receive messages. You can use the message type constants at the top of the library file to determine what sort of MIDI message you received:

```python
while True:
    msg = midi_in.receive()
    if not msg:
        continue

    if msg.type == midi.NOTE_ON:
        channel = msg.channel
        note = msg.data[0]
        velocity = msg.data[1]
        print('Note On, Channel: {}, Note: {}, Velocity: {}'.format(
            channel, note, velocity))
    elif msg.type == midi.NOTE_OFF:
        note = msg.data[0]
        velocity = msg.data[1]
        print('Note Off, Channel: {}, Note: {}, Velocity: {}'.format(
            channel, note, velocity))
    elif msg.type == midi.SYSTEM_RESET:
        print('System reset')
```

### System exclusive messages

This library has basic for system exclusive messages. To get a system exclusive message you must check for the `SYSEX` message and then call `receive_sysex` to get the data for the payload. If you don't call `receive_sysex` the payload will be discarded on the next call to `receive`. `receive_sysex` requires you to pass the maximum number of bytes to read from the payload. Any remaining bytes will be discarded.

```python
while True:
    msg = midi_in.receive()
    if not msg:
        continue

    if msg.type == midi.SYSEX:
        sysex_payload, truncated = midi_in.receive_sysex(128)
        print('Got sysex of length {}, Truncated: {}'.format(
            len(sysex_payload, 128)))

```

In the future, I may add the ability to read the sysex messages in chunks if that's something folks desire.

### No MidiOut?

The built-in [PortOut](https://circuitpython.readthedocs.io/en/latest/shared-bindings/usb_midi/PortOut.html) is more than usable enough at a low-level. For example, you can use the constants defined here to send a Note On message:

```python
port_out = usb_midi.ports[0]
port_out.write(bytearray([smolmidi.NOTE_ON, 0x64, 0x42]))
```

So at this point I don't feel like it needs an additional library to wrap it, but, if you have ideas I'd love to hear them. :)

## Installation

Install this library by copying [winterbloom_smolmidi.py](winterbloom_smolmidi.py) to your device's `lib` folder.

## License and contributing

This is available under the [MIT License](LICENSE). I welcome contributors, please read the [Code of Conduct](CODE_OF_CONDUCT.md) first. :)
