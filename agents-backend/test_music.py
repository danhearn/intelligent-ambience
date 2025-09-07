from tools.music_generation_tools import StableAudioSmall

if __name__ == "__main__":
    print("Testing StableAudioSmall class directly...")
    generator = StableAudioSmall()
    result = generator.generate_music("relaxed ambient music for rainy day", 11)
    print(f"Result: {result}")