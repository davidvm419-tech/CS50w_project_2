# CS50W Project 2: Commerce

This is my implementation of CS50W’s Project 2. 
The application allows users to create accounts, browse listings, create new listings, add products to a watchlist, place bids, and view detailed information for each active product in the auction.

[!WARNING]
## Disclaimer: 
All images, logos, and product descriptions related to *World of Warcraft* are the property of **Blizzard Entertainment**. They are used **entirely for non‑commercial, educational purposes** within the context of this project. This project is not affiliated with or endorsed by Blizzard Entertainment.
---

## Features

### 1. Models
Five models — **AuctionListing**, **AuctionComment**, **Bid**, **User**, and **WatchList** manage the entire information flow of the application.

### 2. Create Listing
Users can create their own listings by providing a title, description, starting bid, category, and image (optional).

### 3. Active Listings Page
Displays every product currently active in the auction, including its name, image, and current price.

### 4. Listing Page
Shows all details of a specific product, including: 
- Name, description, and auction status (open or closed) 
- Current price and the option to place a higher bid 
- Ability to add or remove the item from the Watchlist 
- Comments section for discussion
The user who created the listing can close the auction at any time.

### 5. Watchlist
Users can add any active product to their Watchlist to keep track of items they are interested in. 

### 6. Categories
Users can browse products by category. Categories are defined in the models. Any new category must be added through the model to ensure proper data flow.

### 7. Django Admin Interface 
A Django superuser can access the admin interface to view, update, or delete any model instance related to the auction.	

Feel free to check it out.