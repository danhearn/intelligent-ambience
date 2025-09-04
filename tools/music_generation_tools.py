import os
from langchain_core.tools import tool
import torch
import soundfile as sf
from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig, StableAudioDiTModel, StableAudioPipeline
from transformers import BitsAndBytesConfig as BitsAndBytesConfig, T5EncoderModel
import numpy as np
from pydub import AudioSegment

class StableAudioSmall: 
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._pipeline = None
        print(f"StableAudioSmall initialized on {self.device}")

    def _load_pipeline(self):
        """Load the diffusers pipeline with 8-bit quantization"""
        if self._pipeline is None:
            print("Loading Stable Audio pipeline with 8-bit quantization...")
            
            # Load quantized text encoder
            quant_config = BitsAndBytesConfig(load_in_8bit=True)
            text_encoder_8bit = T5EncoderModel.from_pretrained(
                "stabilityai/stable-audio-open-1.0",
                subfolder="text_encoder",
                quantization_config=quant_config,
                torch_dtype=torch.float16,
            )

            # Load quantized transformer
            quant_config = DiffusersBitsAndBytesConfig(load_in_8bit=True)
            transformer_8bit = StableAudioDiTModel.from_pretrained(
                "stabilityai/stable-audio-open-1.0",
                subfolder="transformer",
                quantization_config=quant_config,
                torch_dtype=torch.float16,
            )

            # Create pipeline
            self._pipeline = StableAudioPipeline.from_pretrained(
                "stabilityai/stable-audio-open-1.0",
                text_encoder=text_encoder_8bit,
                transformer=transformer_8bit,
                torch_dtype=torch.float16,
                device_map="balanced",
            )
            print(f"Pipeline loaded on device: {self._pipeline.device}")

    def generate_music(self, prompt: str, duration: int = 11, file_name: str = "output", output_dir="generated_tracks") -> str:
        """Generate music using the Diffusers StableAudio pipeline"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            if self._pipeline is None:
                self._load_pipeline()

            duration = min(duration, 45)
            
            audio = self._pipeline(
                prompt=prompt,
                negative_prompt="Low quality, distorted, noisy",
                num_inference_steps=50,
                audio_end_in_s=float(duration),
                num_waveforms_per_prompt=1,
                generator=torch.Generator(device="cuda").manual_seed(42),
            ).audios

            output_audio = audio[0].T.float().cpu().numpy()
            file_path = os.path.join(output_dir, file_name)
            sf.write(file_path, output_audio, self._pipeline.vae.sampling_rate)
            return f"prompt: {prompt}, duration: {duration}, generated music: {file_name}"
            
        except Exception as e:
            print(f"Error generating music: {e}")
            return f"Error generating music: {str(e)}"

stable_audio_small = StableAudioSmall()

@tool
def generate_music(prompt: str, duration: int = 11, file_name: str = "output", output_dir="generated_tracks") -> str:
    """Generate music using the StableAudio Diffusers pipeline
        Args:
            prompt: The prompt to generate music for
            duration: The duration of the music to generate. MAXIMUM 45 seconds.
            file_name: The name of the file to save the generated music to. Include .wav extension.
            output_dir: The directory to save the generated music to.
        Returns:
            A string with the prompt, duration, and the path to the generated music
    """
    music = stable_audio_small.generate_music(prompt, duration, file_name, output_dir)
    return music

@tool
def overlay_audio_files(file_names: list[str], dir_path: str = "generated_tracks") -> str:
    """Merge audio files into a single file. Only use this tool ONCE after all the audio files have been generated.
        Args:
            file_names: A list of file names to merge
            dir_path: Directory where the individual files are located
        Returns:
            A string with the path to the merged file
    """
    try:
        audio_files = [AudioSegment.from_file(os.path.join(dir_path, file_name)) for file_name in file_names]
        combined_audio = audio_files[0]
        for audio_file in audio_files[1:]:
            combined_audio = combined_audio.overlay(audio_file)
        combined_audio.export("combined_audio.wav", format="wav")
        
        # Clean up individual files
        for file_name in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, file_name))
        return "combined_audio.wav"
    except Exception as e:
        return f"Error merging audio files: {str(e)}"

def get_generate_music_tools():
    tools = []
    tools.append(generate_music)
    tools.append(overlay_audio_files)
    return tools