from pinscrape import scraper

keyword = "messi"
output_folder = "output"
proxies = {}
number_of_workers = 10
images_to_download = 100

def using_search_engine():
    details = scraper.scrape(keyword, output_folder, proxies, number_of_workers, images_to_download)
    if details["isDownloaded"]:
        print("\nDownloading completed !!")
        print(f"\nTotal urls found: {len(details['extracted_urls'])}")
        print(f"\nTotal images downloaded (including duplicate images): {len(details['urls_list'])}")
        print(details)
    else:
        print("\nNothing to download !!", details)
    
if __name__ == "__main__":
    using_search_engine()
