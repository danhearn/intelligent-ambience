import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_graph import MainGraph

def main():
    main_graph = MainGraph()
    while True:
        try:
            query = input("Enter a query: ")
            img_url = input("Enter an image URL: ")
            main_graph.run_with_feedback_streaming(query, img_url=img_url)
        except KeyboardInterrupt:
            break       
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()