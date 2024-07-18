from Impeller.train import train
from Impeller.config import create_args
from Impeller.data import download_example_data, load_and_process_example_data

def main():
    download_example_data()
    data, val_mask, test_mask, x, original_x = load_and_process_example_data()
    args = create_args()
    test_l1_distance, test_cosine_sim, test_rmse = train(args, data, val_mask, test_mask, x, original_x)

if __name__ == "__main__":
    main()