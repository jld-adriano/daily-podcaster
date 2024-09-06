import sys
from podcast_generator import generate_podcast

def main():
    if len(sys.argv) < 2:
        print('Usage: python cli_test.py interest1 interest2 ...')
        sys.exit(1)
    
    interests = sys.argv[1:]
    print(f'Generating podcast for interests: {interests}')
    
    podcast = generate_podcast(interests)
    print(f'Podcast generated successfully!')
    print('Transcript:')
    print(podcast['transcript'])

if __name__ == '__main__':
    main()
