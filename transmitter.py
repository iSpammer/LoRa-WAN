import numpy as np


def Generate_LoRa_Signals(SIR, Delay, Signal_File, Interf_File, BW, SF, CR, Over_Sample, F_Shift_Tx, Pkt_Size,
                          Phase_Cont, Load_Sym):
    T = 1 / BW
    Ts = 2 ** SF * T
    Delay = Delay * Ts;
    """Delay between signal and interference """

    k = 1.0 / Over_Sample * np.arange(Over_Sample * 2 ** int(SF))

    Basis_Sym = np.exp(1j * 2 * np.pi * k * k / 2 / (2 ** SF)) * np.exp(-1j * 2 * np.pi * BW / 2 * k * T)
    Downchirp_Sym = np.conjugate(Basis_Sym)

    if not Load_Sym:
        LoRa_Sym_Trace = np.zeros(Pkt_Size)
    else:
        Loaded_LoRa_Trace = Signal_File
        Loaded_Interf_Trace = Interf_File
        Pkt_Size = np.size(Loaded_LoRa_Trace)
        LoRa_Sym_Trace = np.zeros(Pkt_Size)

    Interf_Sym_Trace = np.zeros(Pkt_Size)
    Output_Trace = []

    Preamble_Sym = Basis_Sym

    LoRa_Trace = np.tile(Preamble_Sym, 8)

    # SYNC Word
    SYNC_Len = 2
    SYNC_WORD = [8, 16]
    for Sym in range(0, SYNC_Len):
        LoRa_Sym = SYNC_WORD[Sym]
        if Phase_Cont:
            Sync_Sym = np.exp(1j * 2 * np.pi * (2 * np.mod(k + LoRa_Sym, 2 ** SF) - k) * (k) / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
        else:
            Sync_Sym = np.exp(1j * 2 * np.pi * (np.mod(k + LoRa_Sym, 2 ** SF)) ** 2 / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
        LoRa_Trace = np.append(LoRa_Trace, Sync_Sym)

    LoRa_Trace = np.append(LoRa_Trace, np.tile(Downchirp_Sym, 2))
    LoRa_Trace = np.append(LoRa_Trace, Downchirp_Sym[0:2 ** (SF - 2) * Over_Sample])

    Interf_Trace = np.tile(Preamble_Sym, 8)

    # SYNC Word
    for Sym in range(0, SYNC_Len):
        LoRa_Sym = SYNC_WORD[Sym]
        if Phase_Cont:
            Sync_Sym = np.exp(1j * 2 * np.pi * (2 * np.mod(k + LoRa_Sym, 2 ** SF) - k) * (k) / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
        else:
            Sync_Sym = np.exp(1j * 2 * np.pi * (np.mod(k + LoRa_Sym, 2 ** SF)) ** 2 / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
        Interf_Trace = np.append(Interf_Trace, Sync_Sym)

    Interf_Trace = np.append(Interf_Trace, np.tile(Downchirp_Sym, 2))
    Interf_Trace = np.append(Interf_Trace, Downchirp_Sym[0:2 ** (SF - 2) * Over_Sample])

    for Sym in range(0, Pkt_Size):
        if not Load_Sym :
            LoRa_Sym = np.random.randint(2 ** SF)
            Interf_Sym = np.random.randint(2 ** SF)
        else:
            LoRa_Sym = Loaded_LoRa_Trace[Sym]
            Interf_Sym = Loaded_Interf_Trace[Sym]
            # Interf_Sym = np.random.randint(2**SF)

        if Phase_Cont :
            Tx_Sym = np.exp(1j * 2 * np.pi * (2 * np.mod(k + LoRa_Sym, 2 ** SF) - k) * (k) / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
            Tx_Interf_Sym = np.exp(
                1j * 2 * np.pi * (2 * np.mod(k + Interf_Sym, 2 ** SF) - k) * (k) / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
        else:
            Tx_Sym = np.exp(1j * 2 * np.pi * (np.mod(k + LoRa_Sym, 2 ** SF)) ** 2 / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)
            Tx_Interf_Sym = np.exp(1j * 2 * np.pi * (np.mod(k + Interf_Sym, 2 ** SF)) ** 2 / 2 / (2 ** SF)) * np.exp(
                -1j * 2 * np.pi * BW / 2 * k * T)

        LoRa_Trace = np.append(LoRa_Trace, Tx_Sym)
        Interf_Trace = np.append(Interf_Trace, Tx_Interf_Sym)

        LoRa_Sym_Trace[Sym] = LoRa_Sym
        Interf_Sym_Trace[Sym] = Interf_Sym

    LoRa_Trace = np.append(LoRa_Trace, np.zeros(int(Delay / T * Over_Sample)))
    Interf_Trace = np.append(np.zeros(int(Delay / T * Over_Sample)), Interf_Trace)

    SIR_Lin = 10 ** (SIR / 10)
    print(SIR_Lin)
    if SIR_Lin < 100.0:
        print("Interference")
        Output_Trace = LoRa_Trace + 1 / np.sqrt(SIR_Lin) * Interf_Trace
        Output_Trace = Output_Trace / np.sqrt(2)
        SIR_Implemeneted = SIR
    else:
        print("No Interference")
        Output_Trace = LoRa_Trace
        Output_Trace = Output_Trace / np.sqrt(2)
        SIR_Implemeneted = 100.0

    Output_Tx = np.complex64(Output_Trace)

    File_Name = "LoRa_Packet_B" + np.str(np.int(BW / 1000)) + "_SF" + np.str(np.int(SF)) + "_CR" + np.str(
        CR) + "_SIR" + np.str(np.double(SIR_Implemeneted)) + "dB_D" + np.str(np.double(Delay / Ts)) + ".dat"

    Output_Tx.tofile(File_Name)
    return File_Name
