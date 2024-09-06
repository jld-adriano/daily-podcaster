from podcast_generator import generate_podcast_stream


def read_user_description():
    with open("user_description.txt", "r") as file:
        return file.read().strip()


def main():
    user_description = read_user_description()
    print(f"Generating podcast for user description: {user_description}")

    try:
        for step in generate_podcast_stream(user_description, "fake_user_id"):
            print(f"Step: {step['step']}")
            print(f"Data: {step['data']}")
            print("---")

        print("Podcast generated successfully!")
    except Exception as e:
        print(f"Error generating podcast: {str(e)}")
        print(e)


if __name__ == "__main__":
    main()
