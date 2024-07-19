from whisper_run import AudioProcessor

def main():
    processor = AudioProcessor(file_path="your_file_path",
                               device="cpu",
                               model_name="large-v3",
                               hf_auth_token="your_hf_token",
                               save=True)
    processor.process()

if __name__ == "__main__":
    main()