
# Syncify: Web Audioplayer for Sync.com

  

![](https://i.imgur.com/C6z3VbC.png)

  

## What is Syncify?

  

Syncify is a web audioplayer built for Sync.com. It allows you to index and request songs on a per-song basis, rather than downloading your entire music library. Syncify is built using a Python Selenium Scraper, a Flask+Socket.io webserver, and a Vue3 frontend.

  

## Features

  

-  **On-Demand Music Streaming:** Index and request individual songs from your Sync.com library.

-  **Local or Remote Access:** Run Syncify locally or host it online on a server.

-  **Multiple Formats Supported:** Supports .opus, .mp3, and .m4a file formats.

  

## How to Setup

  

1.  **Create a Public Shared Folder:**

- In Sync.com, create a public shared folder in your vault containing your music files.

  

2.  **Configure Selenium Helper:**

- Assign the public shared folder link in the Selenium helper script.

  

3.  **Run Syncify:**

- Start the application with `python app.py`.

  

4.  **Run Development Environment:**

- Navigate to the `ui` folder.

- Build the Vue project with `npm run build`.

  

## Limitations and Acknowledgements

  

-  **Web UI Changes:** If Sync.com drastically changes their web UI, the scraper will need to be updated.

-  **Single User Streaming:** The Socket.io server serves the same music to all instances on the server, so multiple users at once are not supported.

-  **Supported Formats:** Only .opus, .mp3, and .m4a formats are supported. Other formats may need to be transcoded.

  

## Technology Stack

  

-  **Backend:** Python, Flask, Socket.io

-  **Frontend:** Vue3

-  **Web Scraping:** Selenium

  

## Contributing

  

Contributions are welcome! Please fork this repository and submit a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

  

## License

  

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

  

## Contact

  

For any questions or support, please open an issue or contact the repository owner.

  

---

  

**Disclaimer:** This project is not affiliated with or endorsed by Sync.com.