from concurrent.futures import ThreadPoolExecutor
def process_image(image):
    pass
def main():
    images = [...]
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_image, images)
if __name__ == "__main__":
    main()