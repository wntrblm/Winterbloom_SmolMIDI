# Copyright (c) 2019 Alethea Flowers for Winterbloom
# Licensed under the MIT License

import pytest

import winterbloom_smolmidi as smolmidi


class PortStub:
    def __init__(self, data):
        self.data = data

    def readinto(self, buf, numbytes):
        bytes_read = 0
        for n in range(numbytes):
            try:
                value = next(self.data)
                if isinstance(value, Exception):
                    raise value

                buf[n] = value
                bytes_read += 1
            except StopIteration:
                break

        return bytes_read


def test__read_n_bytes_empty():
    port = PortStub(iter([]))
    buf = bytearray()
    dest = []

    smolmidi._read_n_bytes(port, buf, dest, 0)
    
    assert dest == []


def test__read_n_bytes_full():
    port = PortStub(iter([1, 2, 3, 4]))
    buf = bytearray(4)
    dest = []

    smolmidi._read_n_bytes(port, buf, dest, 4)
    
    assert dest == [1, 2, 3, 4]

def test__read_n_bytes_chunked():
    port = PortStub(iter([1, 2, StopIteration(), 3, 4]))
    buf = bytearray(4)
    dest = []

    smolmidi._read_n_bytes(port, buf, dest, 4)
    
    assert dest == [1, 2, 3, 4]


def test_midi_in_empty():
    port = PortStub(iter([]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg is None


def test_midi_in_invalid_data():
    # A port with non-status leading bytes
    port = PortStub(iter([0x01]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg is None


def test_midi_in_no_data():
    # A port with a midi tick.
    port = PortStub(iter([smolmidi.TICK]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg.type == smolmidi.TICK
    assert msg.channel == None
    assert bytes(msg) == bytes([smolmidi.TICK])


def test_midi_in_one_data_byte():
    # A port with a program change message.
    port = PortStub(iter([smolmidi.PROGRAM_CHANGE | 0x02, 0x42]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg.type == smolmidi.PROGRAM_CHANGE
    assert msg.channel == 0x02
    assert msg.data[0] == 0x42
    assert bytes(msg) == bytes([smolmidi.PROGRAM_CHANGE | 0x02, 0x42])


def test_midi_in_two_data_bytes():
    # A port with a Note On message.
    port = PortStub(iter([smolmidi.NOTE_ON | 0x01, 0x64, 0x42]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg.type == smolmidi.NOTE_ON
    assert msg.channel == 0x01
    assert msg.data[0] == 0x64
    assert msg.data[1] == 0x42


def test_midi_in_running_status():
    # A port with a Note On message followed by another with running status.
    port = PortStub(iter([smolmidi.NOTE_ON | 0x01, 0x64, 0x42, 0x65, 0x43]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg.type == smolmidi.NOTE_ON
    assert msg.channel == 0x01
    assert msg.data[0] == 0x64
    assert msg.data[1] == 0x42
    msg = midi_in.receive()

    assert msg.type == smolmidi.NOTE_ON
    assert msg.channel == 0x01
    assert msg.data[0] == 0x65
    assert msg.data[1] == 0x43


def test_midi_in_sysex_receive():
    port = PortStub(iter([smolmidi.SYSEX, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, smolmidi.SYSEX_END]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg.type == smolmidi.SYSEX

    sysex_msg, truncated = midi_in.receive_sysex(128)

    assert sysex_msg == bytearray([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert not truncated



def test_midi_sysex_discard():
    port = PortStub(iter([smolmidi.SYSEX, 1, smolmidi.SYSEX_END, smolmidi.NOTE_ON | 0x01, 0x64, 0x42]))
    midi_in = smolmidi.MidiIn(port)

    msg = midi_in.receive()

    assert msg.type == smolmidi.SYSEX

    msg = midi_in.receive()
    
    assert msg.type == smolmidi.NOTE_ON
    assert msg.channel == 0x01
    assert msg.data[0] == 0x64
    assert msg.data[1] == 0x42