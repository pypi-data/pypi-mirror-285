import pickle
from pathlib import Path

import haplo.data_preparation

from gobo.corner_plot import create_multi_distribution_corner_plot


def main():
    # Load the dataframes.
    physical_model_data_path = Path('data/mcmc_vac_all_f90_physical1_new_ref_no_cuts.pkl')
    neural_network_data_path = Path('data/mcmc_vac_all_f90_2024_05_17_16_05_30_1000_bs_001_lr_32'
                                    '_node_2_gpu_44_cpu_1_pp_500m_third_cont_5_23.dat')
    physical_model_data_frame = pickle.load(physical_model_data_path.open('rb'))
    if neural_network_data_path.with_suffix('.pkl').exists():
        neural_network_data_frame = pickle.load(neural_network_data_path.with_suffix('.pkl').open('rb'))
    else:
        neural_network_data_frame = haplo.data_preparation.arbitrary_constantinos_kalapotharakos_file_handle_to_polars(
            neural_network_data_path, columns_per_row=14).to_pandas()
        pickle.dump(neural_network_data_frame, neural_network_data_path.with_suffix('.pkl').open('wb'))
    # Get the parameters subset of the columns.
    physical_model_array = physical_model_data_frame.values[:, :11]
    neural_network_array = neural_network_data_frame.values[:, :11]
    # Get only the last N states of the shorter data frame. Get the same range from the other.
    end_state_index = min(physical_model_array.shape[0], neural_network_array.shape[0])
    number_of_states_to_include = 100_000
    start_state_index = end_state_index - number_of_states_to_include
    physical_model_partial_array = physical_model_array[start_state_index:end_state_index]
    neural_network_partial_array = neural_network_array[start_state_index:end_state_index]
    # Create the distribution comparison plot.
    create_multi_distribution_corner_plot([physical_model_partial_array, neural_network_partial_array])


if __name__ == '__main__':
    main()
