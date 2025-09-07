import os
from langchain_core.tools import tool
import torch
import soundfile as sf
from diffusers import BitsAndBytesConfig as DiffusersBitsAndBytesConfig, StableAudioDiTModel, StableAudioPipeline
from transformers import BitsAndBytesConfig as BitsAndBytesConfig, T5EncoderModel
import numpy as np
from pydub import AudioSegment

# Fixed output directory - always use this same directory
OUTPUT_DIR = "generated_tracks"

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

    def generate_music(self, prompt: str, duration: int = 11, file_name: str = "output", output_dir: str = OUTPUT_DIR) -> str:
        """Generate music using the Diffusers StableAudio pipeline"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            if self._pipeline is None:
                self._load_pipeline()

            duration = min(duration, 15)
              
            audio = self._pipeline(
                prompt=prompt,
                negative_prompt="Low quality, distorted, noisy",
                num_inference_steps=50,
                audio_end_in_s=float(duration),
                num_waveforms_per_prompt=1,
                generator=torch.Generator(device=self.device).manual_seed(42),
            ).audios

            output_audio = audio[0].T.float().cpu().numpy()
            
            # Ensure file has .wav extension
            if not file_name.endswith('.wav'):
                file_name += '.wav'
                
            file_path = os.path.join(output_dir, file_name)
            sf.write(file_path, output_audio, self._pipeline.vae.sampling_rate)
            
            return f"prompt: {prompt}, duration: {duration}, generated music: {file_name}"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error generating music: {str(e)}"

stable_audio_small = StableAudioSmall()

@tool
def generate_music(prompt: str, duration: int = 11, file_name: str = "output") -> str:
    """Generate music using the StableAudio Diffusers pipeline
        Args:
            prompt: The prompt to generate music for
            duration: The duration of the music to generate. MAXIMUM 15 seconds.
            file_name: The name of the file to save the generated music to. Include .wav extension.
        Returns:
            A string with the prompt, duration, and the path to the generated music
    """
    # Always use the same output directory
    output_dir = OUTPUT_DIR
    music = stable_audio_small.generate_music(prompt, duration, file_name, output_dir)
    return music

@tool
def overlay_audio_files(file_names: list[str]) -> str:
    """Merge audio files into a single file. Only use this tool ONCE after all the audio files have been generated.
        Args:
            file_names: A list of file names to merge
        Returns:
            A string with the path to the merged file
    """
    # Always use the same directory
    dir_path = OUTPUT_DIR
    try:
        print(f"🎵 Merging {len(file_names)} audio files...")
        
        # Check if all files exist
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            if not os.path.exists(file_path):
                return f"Error: File {file_name} not found in {dir_path}"
        
        audio_files = [AudioSegment.from_file(os.path.join(dir_path, file_name)) for file_name in file_names]
        combined_audio = audio_files[0]
        
        for i, audio_file in enumerate(audio_files[1:], 1):
            print(f"  Adding track {i+1}/{len(audio_files)}...")
            combined_audio = combined_audio.overlay(audio_file)
        
        # Export combined audio
        combined_path = "combined_audio.wav"
        combined_audio.export(combined_path, format="wav")
        print(f"✅ Combined audio saved to: {combined_path}")
        
        # Clean up individual files
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Cleaned up: {file_name}")
        
        return combined_path
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error merging audio files: {str(e)}"

def get_generate_music_tools():
    tools = []
    tools.append(generate_music)
    tools.append(overlay_audio_files)
    return tools