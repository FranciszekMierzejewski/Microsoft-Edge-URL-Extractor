import re
import os
import sqlite3

# To find recent session data, Win + R, %localappdata%\Microsoft\Edge\User Data\Default\Sessions

class ExtractHistory():

    def __init__(self, database, output_file):

        """
        Initialise the ExtractHistory object

        Args: 
            database (str): Path of Edge SQLite database/session file
            output_file (str): Path of text file to save extracted URLs
        """

        self.database, self.output_file = self._sanitise_path(database, output_file)

    
    def _sanitise_path(self, database, output_file):

        """
        Strip input paths of whitespace and quotations, since they are automatically included when copying path

        Args:
            database (str): Path of Edge SQLite database/session file
            output_file (str): Path of text file to save extracted URLs

        Returns:
            (tuple): Sanitised paths
        """

        return database.strip().strip('"').strip("'"), output_file.strip().strip('"').strip("'")


    def _save_urls(self, urls):

        """
        Save a list of URLs to output file

        Args:
            urls (list/set): List of URL strings to save
        """

        with open(self.output_file, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(f"{url}\n")


    def recent_tab_session(self):
        """
        Extract URLs from a recent Edge session file ordered by last visit time and save to the output file

        Returns:
            unique_urls (set): Unique URLs extracted from the session
        """

        with open(self.database, "rb") as f:
            extracted_data = f.read()

        decoded_data = extracted_data.decode("latin-1")
        urls = re.findall(r"https?://[\w\-._~:/?#\[\]@!$&'()*+,;=%]+", decoded_data)

        unique_urls = set(urls) # removes dupes, assumes order isn't a priority
        self._save_urls(unique_urls)

        print(f"Extracted {len(unique_urls)} URLs. Saved to {self.output_file}")
        return unique_urls


    def all_history(self):
        """
        Extract URLs from entire browsing history and save to the output file

        Returns:
            urls (list): URLs extracted from the SQLite database
        """
                
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()

            cursor.execute("SELECT url FROM urls ORDER BY last_visit_time DESC")
            rows = cursor.fetchall()
            
            urls = [url for url in rows]
            self._save_urls(urls)

            conn.close()

            print(f"Extracted {len(rows)} URLs. Saved to {self.output_file}")
            return urls

        except sqlite3.DatabaseError as e:
            print("File is not a database!")


def main():
    """
    Main function to prompt user for database/session path, output path and choice.
    """

    database_input = input("Please enter file path containing historical data: ")
    output_file_input = input("Please enter file path for text file to save extracted URLs in: ")
    sample = ExtractHistory(database_input, output_file_input)

    choice = input("Enter 1 to extract URLs for Recent Session, or 2 for All History: ")

    if choice == "1":
        sample.recent_tab_session()
    elif choice == "2":
        sample.all_history()
    else:
        print("Invalid selection")


if __name__ == "__main__":
    main()