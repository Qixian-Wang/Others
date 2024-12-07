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

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

local_tmp_dir = f"/tmp/data_rank_{rank}"
os.makedirs(local_tmp_dir, exist_ok=True)
shared_data_path = "/scratch1/10197/qxwang/NWB_MPI/RecordNode103__experiment1__recording1.nwb"
local_data_path = os.path.join(local_tmp_dir, "recording1.nwb")
shutil.copy(shared_data_path, local_data_path)

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
    lfp_gen = lfp_signal_generator(lfp_series, num_chunks, rank, size)

    spike_series = nwbfile.acquisition["Spike Events"]
    spike_gen = spike_train_generator(spike_series, num_chunks, rank, size, segment_length=60)

    chunk_limit = 5
    channel_limit = 5
    chunk = rank

    signal_summary_file_path = "./signal_analysis"

    while chunk < chunk_limit:
        signal_chunk = next(lfp_gen)
        plot_path_chunk = os.path.join(plot_tmp_dir, f"lfp_chunk{chunk: 03d}")
        os.makedirs(plot_path_chunk, exist_ok=True)

        for channel in range(channel_limit):
            plt.figure(figsize=(10, 4))
            plt.plot(signal_chunk.timestamps, signal_chunk.data[:, channel])
            plt.title("LFP Signal")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid()
            plot_path_channel = os.path.join(plot_path_chunk, f"lfp_figure_channel{channel}.png")
            plt.savefig(plot_path_channel, dpi=300)
            plt.close()

        print(f"lfp: rank {rank} handled chunk {chunk}")
        chunk += size

    chunk = rank
    spike_summary_file_path = "./spike_analysis"
    while chunk < chunk_limit:
        spike_chunk = next(spike_gen)
        plot_path_chunk = os.path.join(plot_tmp_dir, f"spike_train_chunk{chunk: 03d}")
        os.makedirs(plot_path_chunk, exist_ok=True)
        for channel, spike_times in enumerate(spike_chunk):
            y_values = [channel] * len(spike_times)
            plt.scatter(spike_times, y_values, s=1, color="blue")

        plt.title(f"Spike Train - All Channels (Chunk {chunk})")
        plt.xlabel("Time (s)")
        plt.ylabel("Channel Index")
        plt.legend(loc='upper right')
        plot_path_channel = os.path.join(plot_path_chunk, f"spike_train_channels.png")
        plt.savefig(plot_path_channel, dpi=300)
        plt.close()

        print(f"spike: rank {rank} handled chunk {chunk}")
        chunk += size

    comm.barrier()
    if rank == 0:
        time_end = MPI.Wtime()
        time = time_end - time_start
        summary_file_path = os.path.join('/scratch1/10197/qxwang/NWB_MPI/', 'summary.txt')
        with open(summary_file_path, 'w') as summary_file:
            summary_file.write(f"data processing time: {time}\n")

    comm.Barrier()

    if rank == 0:
        os.makedirs(final_gather_dir, exist_ok=True)

    comm.Barrier()

    if rank != 0:
        shutil.copytree(plot_tmp_dir, os.path.join(final_gather_dir, f"rank_{rank}"))
        print(f"Rank {rank}: Files sent to master node")
    else:
        shutil.copytree(plot_tmp_dir, os.path.join(final_gather_dir, f"rank_{rank}"))

    comm.Barrier()

    if rank == 0:
        zip_file_path = os.path.join(final_output_dir, "plots_gathered.zip")
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(final_gather_dir):
                for file in files:
                    zipf.write(os.path.join(root, file),
                               arcname=os.path.relpath(os.path.join(root, file), final_gather_dir))
        print(f"Master node: All plots compressed to {zip_file_path}")

    shutil.rmtree(local_tmp_dir)
    shutil.rmtree(plot_tmp_dir)
