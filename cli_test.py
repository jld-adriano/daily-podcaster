from podcast_generator import generate_podcast

def read_user_description():
    with open('user_description.txt', 'r') as file:
        return file.read().strip()

def main():
    user_description = read_user_description()
    print(f'Generating podcast for user description: {user_description}')
    
    podcast = generate_podcast(user_description)
    print(f'Podcast generated successfully!')
    print('Transcript:')
    print(podcast['transcript'])

if __name__ == '__main__':
    main()
