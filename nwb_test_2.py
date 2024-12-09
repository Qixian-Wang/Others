import os

import shutil
import zipfile
from mpi4py import MPI
from pynwb import NWBHDF5IO
import numpy as np
import matplotlib.pyplot as plt
from pynwb import NWBHDF5IO

from miv.datasets.openephys_sample import load_data
from miv.core.datatype import Signal, Spikestamps

class signal_generating:

    def __init__(self, num_chunks, num_channels, total_signal, plot_tmp_dir):
        self.plot_tmp_dir = plot_tmp_dir
        self.num_chunks = num_chunks
        self.num_channels = num_channels
        self.total_signal = total_signal


    def lfp_signal_generator(self, lfp_series, total_signal, rank, size):
        sampling_rate = lfp_series.rate

        for signl_idx in range(rank, total_signal, size):
            self.chunk_index = signl_idx // self.num_channels
            self.channel_index = signl_idx % self.num_channels
            lfp_data = lfp_series.data[self.chunk_index, :, self.channel_index]
            lfp_data = lfp_data[:, np.newaxis]
            timestamps = np.linspace(
                self.chunk_index * len(lfp_data) / sampling_rate,
                (self.chunk_index + 1) * len(lfp_data) / sampling_rate,
                len(lfp_data)
            )

            yield Signal(
                data=lfp_data,
                timestamps=timestamps,
                rate=sampling_rate
            )


    def spike_train_generator(self, spike_series, total_signal, rank, size, segment_length=60):
        spike_timestamps = spike_series.timestamps[:]

        for signl_idx in range(rank, total_signal, size):
            self.chunk_index = signl_idx // self.num_channels
            self.channel_index = signl_idx % self.num_channels

            start_time = self.chunk_index * segment_length
            end_time = start_time + segment_length

            start_idx = np.searchsorted(spike_timestamps, start_time, side="left")
            end_idx = np.searchsorted(spike_timestamps, end_time, side="right")
            time_matrix = []

            channel_timestamps = spike_timestamps[start_idx:end_idx]
            channel_spikes = spike_series.data[start_idx:end_idx, self.channel_index]
            valid_mask = channel_spikes > 0
            valid_timestamps = channel_timestamps[valid_mask]

            time_matrix.append(valid_timestamps)

            yield Spikestamps(time_matrix)


    def plot_lfp(self, lfp_series, total_signal, rank, size):
        lfp_gen = self.lfp_signal_generator(lfp_series, total_signal, rank, size)

        current_index = rank
        while current_index < self.total_signal:
            signal_chunk = next(lfp_gen)
            plot_path_chunk = os.path.join(self.plot_tmp_dir, f"lfp_chunk{self.chunk_index: 03d}")
            os.makedirs(plot_path_chunk, exist_ok=True)

            plt.figure(figsize=(10, 4))
            plt.plot(signal_chunk.timestamps, signal_chunk.data)
            plt.title("LFP Signal")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plot_path_channel = os.path.join(plot_path_chunk, f"lfp_figure_channel{self.channel_index}.png")
            plt.savefig(plot_path_channel, dpi=300)
            plt.close()

            print(f"lfp: rank {rank} handled chunk {self.chunk_index} channel {self.channel_index}")
            current_index += size

    def plot_spike_train(self, spike_series, num_chunks, rank, size):
        spike_gen = self.spike_train_generator(spike_series, num_chunks, rank, size)

        current_index = rank
        while current_index < self.total_signal:
            spike_chunk = next(spike_gen)
            plot_path_chunk = os.path.join(plot_tmp_dir, f"spike_train_chunk{self.chunk_index: 03d}")
            os.makedirs(plot_path_chunk, exist_ok=True)
            for spike_times in spike_chunk:
                y_values = np.zeros(len(spike_times))
                plt.scatter(spike_times, y_values, s=1, color="blue")

            plt.title(f"Spike Train - All Channels (Chunk {self.chunk_index})")
            plt.xlabel("Time (s)")
            plt.ylabel("Channel Index")
            plot_path_channel = os.path.join(plot_path_chunk, f"spike_train_channel {self.channel_index}.png")
            plt.savefig(plot_path_channel, dpi=300)
            plt.close()

            print(f"spike: rank {rank} handled chunk {self.chunk_index} channel {self.channel_index}")
            current_index += size

local_tmp_dir = f"/tmp/data_rank"
os.makedirs(local_tmp_dir, exist_ok=True)
# data_path = "/Users/aia/Downloads/RecordNode103__experiment1__recording1.nwb"
# data_path = "/scratch1/10197/qxwang/NWB_MPI/RecordNode103__experiment1__recording1.nwb"
data_path = "/scratch1/10197/qxwang/NWB_MPI/RecordNode115__experiment1__recording1.nwb"
local_data_path = os.path.join(local_tmp_dir, "recording1.nwb")
shutil.copy(data_path, local_data_path)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

plot_tmp_dir = f"/tmp/plots_rank_{rank}"
os.makedirs(plot_tmp_dir, exist_ok=True)

final_gather_dir = "/tmp/all_plots_gathered"
final_output_dir = "/scratch1/10197/qxwang/NWB_MPI/zip_plot_file"
os.makedirs(final_output_dir, exist_ok=True)

comm.Barrier()

with NWBHDF5IO(local_data_path, mode="r", comm=comm) as io:
    nwbfile = io.read()

    time_start = MPI.Wtime()
    # read data
    lfp_interface = nwbfile.processing["ecephys"].data_interfaces["LFP"]
    lfp_series = lfp_interface.electrical_series["ElectricalSeries"]
    num_chunks = lfp_series.data.shape[0]
    num_channels = lfp_series.data.shape[2]
    total_signal = num_chunks * num_channels

    # plot_tmp_dir = "./analysis"

    analysis = signal_generating(num_chunks, num_channels, total_signal, plot_tmp_dir)
    lfp_process = analysis.plot_lfp(lfp_series, total_signal, rank, size)


    spike_series = nwbfile.acquisition["Spike Events"]
    spike_process = analysis.plot_spike_train(spike_series, num_chunks, rank, size)


comm.barrier()
if rank == 0:
    time_end = MPI.Wtime()
    processtime = time_end - time_start
    time_save_start = MPI.Wtime()

comm.Barrier()
procs_per_node = size // 18
is_node_master = (rank % procs_per_node == 0)

if is_node_master:
    os.makedirs(final_gather_dir, exist_ok=True)
    shutil.copytree(plot_tmp_dir, os.path.join(final_gather_dir, f"rank_{rank}"))
else:
    path_local = os.path.join(final_gather_dir, f"rank_{rank}")
    shutil.copytree(plot_tmp_dir, path_local)

comm.Barrier()

if is_node_master:

    zip_file_path = os.path.join(final_output_dir, f"plots_gathered_rank{rank}.zip")
    file_count = 0
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(final_gather_dir):
            for file in files:
                zipf.write(os.path.join(root, file),
                           arcname=os.path.relpath(os.path.join(root, file), final_gather_dir))
                file_count += 1
    print(f"Master node: All plots compressed to {zip_file_path}")
    print(f"Total files saved and compressed: {file_count}")

if rank == 0:

    time_save_end = MPI.Wtime()
    time_save = time_save_end - time_save_start
    summary_file_path = os.path.join('/scratch1/10197/qxwang/NWB_MPI/', 'summary.txt')
    with open(summary_file_path, 'w') as summary_file:
        summary_file.write(f"data processing time: {processtime}\n")
        summary_file.write(f"time for saving: {time_save}\n")
        summary_file.write(f"total time: {time_save + processtime}\n")
        summary_file.write(f"total signal: {total_signal}")