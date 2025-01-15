import asyncio
import os
from crawl4ai import AsyncWebCrawler

# FLOW DESCRIPTION:
# PHASE 1: Initial URL Collection
# 1. Set the start URL and base domain.
# 2. Crawl the main page and save its content to data.md in the .md directory inside the root folder.
# 3. Extract all internal links from the main page and add them to the pending_urls set.

# PHASE 2: Process Each URL (Main Loop)
# 1. While there are URLs in pending_urls:
#    a. Take a batch of URLs for parallel processing (up to 5 at a time).
#    b. Crawl the batch of URLs concurrently using arun_many.
#    c. Append their content to data.md in the .md directory.
#    d. Extract internal links from each crawled page.
#    e. Add new internal links to pending_urls, skipping already visited links.

async def crawl_with_internal_links(start_url):
    async with AsyncWebCrawler() as crawler:
        pending_urls = {start_url}
        visited_urls = set()

        # Create a directory to store the consolidated markdown file
        output_dir = ".md"
        os.makedirs(output_dir, exist_ok=True)
        consolidated_file = os.path.join(output_dir, "data.md")

        # Clear the consolidated file if it exists
        with open(consolidated_file, "w", encoding="utf-8") as file:
            file.write(f"# Consolidated Data\n\n")

        while pending_urls:
            # Take up to 5 URLs for parallel processing
            current_batch = list(pending_urls)[:5]
            for url in current_batch:
                pending_urls.remove(url)

            visited_urls.update(current_batch)

            print(f"Crawling batch: {current_batch}")
            try:
                # Crawl the batch of URLs concurrently
                results = await crawler.arun_many(urls=current_batch)
                for result in results:
                    if result.success:
                        # Append the page content to the consolidated markdown file
                        with open(consolidated_file, "a", encoding="utf-8") as file:
                            file.write(f"## {result.url}\n\n")
                            file.write(result.markdown)
                            file.write("\n\n---\n\n")  # Separator between pages

                        # Extract internal links
                        internal_links = [link['href'] for link in result.links.get('internal', [])]
                        for link in internal_links:
                            # Handle relative paths
                            if not link.startswith("http"):
                                link = start_url.rstrip("/") + "/" + link.lstrip("/")
                            # Add to pending_urls if not visited
                            if link not in visited_urls and link not in pending_urls:
                                pending_urls.add(link)
                    else:
                        print(f"Failed to crawl {result.url}: {result.error_message}")
            except Exception as e:
                print(f"Error during batch crawling: {e}")

# Main execution
if __name__ == "__main__":
    start_url = "https://docs.crawl4ai.com/"
    asyncio.run(crawl_with_internal_links(start_url))
