import subprocess
import time
import serial
import numpy as np
import transmitter as Tx_Fn
import os


def send_lora():
    BW = 125000.0
    SF = 9.0
    Over_Sample = 16
    Pkt_Size = 50
    SIR_Mat = [1.0];
    Delay_Mat = [0]
    # Delay_Mat = 0.0+np.arange(170)*0.25
    Gain_Mat = [16.5]
    serial_port = 'COM8';
    baud_rate = 9600;
    stream_time = 20;
    CR = 1
    if CR == 3:
        Signal_File = "Hello_World_Syms_47.bin"
    else:
        Signal_File = "Hello_World_Syms.bin"
    for Gain_Index in range(0, np.size(Gain_Mat)):
        Gain = Gain_Mat[Gain_Index]
        for SIR_Index in range(0, np.size(SIR_Mat)):
            SIR = SIR_Mat[SIR_Index]
            for Delay_Index in range(0, np.size(Delay_Mat)):
                Delay = Delay_Mat[Delay_Index]
            print(Gain)
            print(SIR)
            print(Delay)
            os.chdir("D:/UHD/lib/uhd/examples")
            SDR_File_Name = Tx_Fn.Generate_LoRa_Signals(SIR, Delay, Signal_File, BW, SF, CR, Over_Sample,
                                                        Pkt_Size)  # Generates .dat file
            if SIR > 20.0:
                SIR = 100.0
            Output_File_Name = "Hello_World_CR" + np.str(CR) + "_SIR" + np.str(SIR) + "dB_D" + np.str(
                Delay) + "_G" + np.str(Gain) + ".txt"
            write_to_file_path = Output_File_Name;
            os.chdir("D:/UHD/lib/uhd/examples")
            process = subprocess.Popen(
                ['tx_samples_from_file.exe', '--args', '"addr=10.3.14.26"', '--file', SDR_File_Name, '--type', 'float',
                 '--rate', '2.0e6', '--freq', '868.130e6', '--bw', '4.0e6', '--gain', np.str(Gain), '--delay', '0.2',
                 '--repeat'])
            output_file = open(write_to_file_path, "w+");
            ser = serial.Serial(serial_port, baud_rate, timeout=2.0)  # Opens the serial port between PC and USB to TTL
            time.sleep(10)

            now = time.time()
            future = now + stream_time

            while time.time() < future:
                line = ser.readline();
                line = line.decode(" utf-8 ")
                output_file.write(line);

            Duration = time.time() - now
            End_Line = np.str(Duration) + ",0,0,0,0,0"
            output_file.write(End_Line);
            ser.close()
            output_file.close()
            process.kill()


