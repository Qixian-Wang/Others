import os

import math
from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
from pynwb import NWBHDF5IO

from miv.core.datatype import Signal, Spikestamps

file_path = "/Users/aia/Downloads/RecordNode103__experiment1__recording1.nwb"

def lfp_signal_generator(lfp_series, num_chunks, rank, size):
    sampling_rate = lfp_series.rate

    for chunk in range(rank, num_chunks, size):
        lfp_data = lfp_series.data[chunk, :, :]

        timestamps = np.linspace(
            chunk * len(lfp_data) / sampling_rate,
            (chunk + 1) * len(lfp_data) / sampling_rate,
            len(lfp_data)
        )

        yield Signal(
            data=lfp_data,
            timestamps=timestamps,
            rate=sampling_rate
        )


def spike_train_generator(spike_series, num_chunks, rank, size, segment_length=60):
    spike_timestamps = spike_series.timestamps[:]
    num_channels = spike_series.data.shape[1]

    print(rank)

    for chunk in range(rank, num_chunks, size):
        start_time = chunk * segment_length
        end_time = start_time + segment_length

        start_idx = np.searchsorted(spike_timestamps, start_time, side="left")
        end_idx = np.searchsorted(spike_timestamps, end_time, side="right")
        time_matrix = []

        for channel in range(num_channels):
            channel_timestamps = spike_timestamps[start_idx:end_idx]
            channel_spikes = spike_series.data[start_idx:end_idx, channel]
            valid_mask = channel_spikes > 0
            valid_timestamps = channel_timestamps[valid_mask]

            time_matrix.append(valid_timestamps)

        yield Spikestamps(time_matrix)


with NWBHDF5IO(file_path, "r") as io:
    nwbfile = io.read()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # read data
    lfp_interface = nwbfile.processing["ecephys"].data_interfaces["LFP"]
    lfp_series = lfp_interface.electrical_series["ElectricalSeries"]
    num_chunks = lfp_series.data.shape[0]
    num_channels = lfp_series.data.shape[2]
    lfp_gen = lfp_signal_generator(lfp_series, num_chunks, rank, size)

    spike_series = nwbfile.acquisition["Spike Events"]
    spike_gen = spike_train_generator(spike_series, num_chunks, rank, size, segment_length=60)

    chunk_limit = num_chunks
    channel_limit = num_channels
    chunk = 0

    signal_summary_file_path = "./signal_analysis"

    while True:
        signal_chunk = next(lfp_gen)
        plot_path_chunk = os.path.join(signal_summary_file_path, f"lfp_chunk{chunk * size + rank: 03d}")
        os.makedirs(plot_path_chunk, exist_ok=True)

        for channel in range(channel_limit):
            plt.figure(figsize=(10, 4))
            plt.plot(signal_chunk.timestamps, signal_chunk.data[:, channel])
            plt.title("LFP Signal")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plot_path_channel = os.path.join(plot_path_chunk, f"lfp_figure_channel{channel}.png")
            os.makedirs(signal_summary_file_path, exist_ok=True)
            plt.savefig(plot_path_channel, dpi=300)
            plt.close()

        chunk += 1

        if chunk == channel_limit:
            break


    chunk_limit = num_chunks
    channel_limit = num_channels
    chunk = 0

    spike_summary_file_path = "./spike_analysis"
    while True:
        spike_chunk = next(spike_gen)
        plot_path_chunk = os.path.join(spike_summary_file_path, f"spike_train_chunk{chunk * size + rank}")
        os.makedirs(plot_path_chunk, exist_ok=True)
        for channel, spike_times in enumerate(spike_chunk):
            y_values = [channel] * len(spike_times)
            plt.scatter(spike_times, y_values, s=1, color="blue")

        plt.title(f"Spike Train - All Channels (Chunk {chunk})")
        plt.xlabel("Time (s)")
        plt.ylabel("Channel Index")
        plt.legend(loc='upper right')
        plot_path_channel = os.path.join(plot_path_chunk, f"spike_train_channels.png")
        os.makedirs(spike_summary_file_path, exist_ok=True)
        plt.savefig(plot_path_channel, dpi=300)
        plt.close()

        chunk += 1
        if chunk == channel_limit:
            break
