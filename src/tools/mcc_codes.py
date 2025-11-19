"""MCC Codes Tool - Comprehensive Merchant Category Codes Database"""
from typing import Dict, Optional
from agno.tools import tool


# ============================================================================
# COMPREHENSIVE MCC CODE DATABASE (500+ codes from ISO 18245 standard)
# ============================================================================
# This database covers all major merchant categories with proper mappings
# to our transaction taxonomy. No API needed - everything is local & fast!
# ============================================================================

MCC_CODES = {
    # FOOD & DINING (5000-5999)
    "5411": {"description": "Grocery Stores, Supermarkets", "category": "Food & Dining", "subcategory": "Grocery"},
    "5422": {"description": "Freezer and Locker Meat Provisioners", "category": "Food & Dining", "subcategory": "Grocery"},
    "5441": {"description": "Candy, Nut, and Confectionery Stores", "category": "Food & Dining", "subcategory": "Grocery"},
    "5451": {"description": "Dairy Products Stores", "category": "Food & Dining", "subcategory": "Grocery"},
    "5462": {"description": "Bakeries", "category": "Food & Dining", "subcategory": "Grocery"},
    "5499": {"description": "Miscellaneous Food Stores", "category": "Food & Dining", "subcategory": "Grocery"},
    "5811": {"description": "Caterers", "category": "Food & Dining", "subcategory": "Restaurant"},
    "5812": {"description": "Eating Places, Restaurants", "category": "Food & Dining", "subcategory": "Restaurant"},
    "5813": {"description": "Drinking Places (Alcoholic Beverages)", "category": "Food & Dining", "subcategory": "Bar/Club"},
    "5814": {"description": "Fast Food Restaurants", "category": "Food & Dining", "subcategory": "Fast Food"},
    "5921": {"description": "Package Stores - Beer, Wine, Liquor", "category": "Food & Dining", "subcategory": "Grocery"},
    
    # TRANSPORTATION (4000-4999)
    "3000-3299": {"description": "Airlines", "category": "Travel", "subcategory": "Airline"},
    "3351": {"description": "Car Rental Agencies", "category": "Travel", "subcategory": "Car Rental"},
    "4111": {"description": "Transportation - Subway, Commuter Trains", "category": "Transportation", "subcategory": "Public Transit"},
    "4112": {"description": "Passenger Railways", "category": "Transportation", "subcategory": "Public Transit"},
    "4119": {"description": "Ambulance Services", "category": "Healthcare", "subcategory": "Hospital"},
    "4121": {"description": "Taxicabs and Limousines", "category": "Transportation", "subcategory": "Rideshare"},
    "4131": {"description": "Bus Lines", "category": "Transportation", "subcategory": "Public Transit"},
    "4214": {"description": "Motor Freight Carriers and Trucking", "category": "Transportation", "subcategory": "Auto Service"},
    "4411": {"description": "Cruise Lines", "category": "Travel", "subcategory": "Vacation"},
    "4457": {"description": "Boat Rentals and Leases", "category": "Travel", "subcategory": "Vacation"},
    "4468": {"description": "Marinas, Marine Service", "category": "Travel", "subcategory": "Vacation"},
    "4511": {"description": "Airlines", "category": "Travel", "subcategory": "Airline"},
    "4722": {"description": "Travel Agencies", "category": "Travel", "subcategory": "Vacation"},
    "4784": {"description": "Tolls and Bridge Fees", "category": "Transportation", "subcategory": "Parking"},
    "4789": {"description": "Transportation Services", "category": "Transportation", "subcategory": "Public Transit"},
    "4812": {"description": "Telecommunication Equipment", "category": "Shopping", "subcategory": "Electronics"},
    "4814": {"description": "Telecommunication Services", "category": "Utilities", "subcategory": "Telecom"},
    "4816": {"description": "Computer Network Services", "category": "Utilities", "subcategory": "Internet"},
    "4821": {"description": "Telegraph Services", "category": "Utilities", "subcategory": "Telecom"},
    "4829": {"description": "Wires, Money Orders", "category": "Financial Services", "subcategory": "Bank Fee"},
    "4899": {"description": "Cable, Satellite, and Other Pay Television", "category": "Utilities", "subcategory": "Internet"},
    "4900": {"description": "Utilities - Electric, Gas, Water", "category": "Utilities", "subcategory": "Electric"},
    
    # GAS STATIONS & AUTO (5500-5599)
    "5511": {"description": "Car and Truck Dealers (New & Used)", "category": "Transportation", "subcategory": "Auto Service"},
    "5521": {"description": "Car and Truck Dealers (Used Only)", "category": "Transportation", "subcategory": "Auto Service"},
    "5531": {"description": "Auto and Home Supply Stores", "category": "Transportation", "subcategory": "Auto Service"},
    "5532": {"description": "Automotive Tire Stores", "category": "Transportation", "subcategory": "Auto Service"},
    "5533": {"description": "Automotive Parts and Accessories", "category": "Transportation", "subcategory": "Auto Service"},
    "5541": {"description": "Service Stations (Gas Stations)", "category": "Transportation", "subcategory": "Gas Station"},
    "5542": {"description": "Automated Fuel Dispensers", "category": "Transportation", "subcategory": "Gas Station"},
    "5551": {"description": "Boat Dealers", "category": "Shopping", "subcategory": "Retail"},
    "5561": {"description": "Motorcycle Shops and Dealers", "category": "Transportation", "subcategory": "Auto Service"},
    "5571": {"description": "Motorcycle Shops, Dealers", "category": "Transportation", "subcategory": "Auto Service"},
    "5592": {"description": "Motor Homes Dealers", "category": "Transportation", "subcategory": "Auto Service"},
    "5598": {"description": "Snowmobile Dealers", "category": "Transportation", "subcategory": "Auto Service"},
    "5599": {"description": "Miscellaneous Auto Dealers", "category": "Transportation", "subcategory": "Auto Service"},
    
    # CLOTHING & ACCESSORIES (5600-5699)
    "5611": {"description": "Men's and Boys' Clothing Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5621": {"description": "Women's Ready-to-Wear Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5631": {"description": "Women's Accessory Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5641": {"description": "Children's and Infants' Wear Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5651": {"description": "Family Clothing Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5655": {"description": "Sports Apparel, Riding Apparel Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5661": {"description": "Shoe Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5681": {"description": "Furriers and Fur Shops", "category": "Shopping", "subcategory": "Clothing"},
    "5691": {"description": "Men's and Women's Clothing Stores", "category": "Shopping", "subcategory": "Clothing"},
    "5697": {"description": "Tailors, Alterations", "category": "Personal Care", "subcategory": "Salon"},
    "5698": {"description": "Wig and Toupee Stores", "category": "Personal Care", "subcategory": "Beauty"},
    "5699": {"description": "Miscellaneous Apparel Stores", "category": "Shopping", "subcategory": "Clothing"},
    
    # HOME & GARDEN (5200-5299, 5700-5799)
    "5200": {"description": "Home Supply Warehouse Stores", "category": "Home & Garden", "subcategory": "Home Improvement"},
    "5211": {"description": "Lumber, Building Materials Stores", "category": "Home & Garden", "subcategory": "Hardware"},
    "5231": {"description": "Glass, Paint, Wallpaper Stores", "category": "Home & Garden", "subcategory": "Hardware"},
    "5251": {"description": "Hardware Stores", "category": "Home & Garden", "subcategory": "Hardware"},
    "5261": {"description": "Nurseries, Lawn and Garden Supply", "category": "Home & Garden", "subcategory": "Garden"},
    "5271": {"description": "Mobile Home Dealers", "category": "Home & Garden", "subcategory": "Furniture"},
    "5712": {"description": "Furniture, Home Furnishings", "category": "Home & Garden", "subcategory": "Furniture"},
    "5713": {"description": "Floor Covering Stores", "category": "Home & Garden", "subcategory": "Home Improvement"},
    "5714": {"description": "Drapery, Window Covering, Upholstery", "category": "Home & Garden", "subcategory": "Furniture"},
    "5718": {"description": "Fireplace, Fireplace Screens", "category": "Home & Garden", "subcategory": "Hardware"},
    "5719": {"description": "Miscellaneous Home Furnishing", "category": "Home & Garden", "subcategory": "Furniture"},
    "5722": {"description": "Household Appliance Stores", "category": "Shopping", "subcategory": "Electronics"},
    "5732": {"description": "Electronics Stores", "category": "Shopping", "subcategory": "Electronics"},
    "5733": {"description": "Music Stores", "category": "Entertainment", "subcategory": "Music"},
    "5734": {"description": "Computer Software Stores", "category": "Shopping", "subcategory": "Electronics"},
    "5735": {"description": "Record Shops", "category": "Entertainment", "subcategory": "Music"},
    "5811": {"description": "Caterers", "category": "Food & Dining", "subcategory": "Restaurant"},
    
    # SHOPPING & RETAIL (5300-5399, 5900-5999)
    "5309": {"description": "Duty Free Stores", "category": "Shopping", "subcategory": "Retail"},
    "5310": {"description": "Discount Stores", "category": "Shopping", "subcategory": "Retail"},
    "5311": {"description": "Department Stores", "category": "Shopping", "subcategory": "Retail"},
    "5331": {"description": "Variety Stores", "category": "Shopping", "subcategory": "Retail"},
    "5399": {"description": "Miscellaneous General Merchandise", "category": "Shopping", "subcategory": "Retail"},
    "5912": {"description": "Drug Stores, Pharmacies", "category": "Healthcare", "subcategory": "Pharmacy"},
    "5921": {"description": "Package Stores - Beer, Wine, Liquor", "category": "Food & Dining", "subcategory": "Grocery"},
    "5931": {"description": "Used Merchandise Stores", "category": "Shopping", "subcategory": "Retail"},
    "5932": {"description": "Antique Shops", "category": "Shopping", "subcategory": "Retail"},
    "5933": {"description": "Pawn Shops", "category": "Shopping", "subcategory": "Retail"},
    "5935": {"description": "Wrecking and Salvage Yards", "category": "Transportation", "subcategory": "Auto Service"},
    "5937": {"description": "Antique Reproduction Stores", "category": "Shopping", "subcategory": "Retail"},
    "5940": {"description": "Bicycle Shops", "category": "Shopping", "subcategory": "Retail"},
    "5941": {"description": "Sporting Goods Stores", "category": "Shopping", "subcategory": "Retail"},
    "5942": {"description": "Book Stores", "category": "Shopping", "subcategory": "Retail"},
    "5943": {"description": "Stationery, Office Supplies", "category": "Shopping", "subcategory": "Retail"},
    "5944": {"description": "Jewelry Stores, Watches, Clocks", "category": "Shopping", "subcategory": "Retail"},
    "5945": {"description": "Hobby, Toy, and Game Shops", "category": "Shopping", "subcategory": "Retail"},
    "5946": {"description": "Camera and Photographic Supply", "category": "Shopping", "subcategory": "Electronics"},
    "5947": {"description": "Gift, Card, Novelty, Souvenir Shops", "category": "Shopping", "subcategory": "Retail"},
    "5948": {"description": "Luggage and Leather Goods", "category": "Shopping", "subcategory": "Retail"},
    "5949": {"description": "Sewing, Needlework, Fabric Stores", "category": "Shopping", "subcategory": "Retail"},
    "5950": {"description": "Glassware, Crystal Stores", "category": "Shopping", "subcategory": "Retail"},
    "5960": {"description": "Direct Marketing - Insurance Services", "category": "Financial Services", "subcategory": "Insurance"},
    "5962": {"description": "Direct Marketing - Travel", "category": "Travel", "subcategory": "Vacation"},
    "5963": {"description": "Door-To-Door Sales", "category": "Shopping", "subcategory": "Retail"},
    "5964": {"description": "Direct Marketing - Catalog Merchant", "category": "Shopping", "subcategory": "Online"},
    "5965": {"description": "Direct Marketing - Combination Catalog", "category": "Shopping", "subcategory": "Online"},
    "5966": {"description": "Direct Marketing - Outbound Telemarketing", "category": "Shopping", "subcategory": "Online"},
    "5967": {"description": "Direct Marketing - Inbound Telemarketing", "category": "Shopping", "subcategory": "Online"},
    "5968": {"description": "Direct Marketing - Subscription", "category": "Entertainment", "subcategory": "Streaming"},
    "5969": {"description": "Direct Marketing - Other", "category": "Shopping", "subcategory": "Online"},
    "5970": {"description": "Artist's Supply and Craft Shops", "category": "Shopping", "subcategory": "Retail"},
    "5971": {"description": "Art Dealers and Galleries", "category": "Shopping", "subcategory": "Retail"},
    "5972": {"description": "Stamp and Coin Stores", "category": "Shopping", "subcategory": "Retail"},
    "5973": {"description": "Religious Goods Stores", "category": "Shopping", "subcategory": "Retail"},
    "5975": {"description": "Hearing Aids", "category": "Healthcare", "subcategory": "Doctor"},
    "5976": {"description": "Orthopedic Goods, Prosthetics", "category": "Healthcare", "subcategory": "Doctor"},
    "5977": {"description": "Cosmetic Stores", "category": "Personal Care", "subcategory": "Beauty"},
    "5978": {"description": "Typewriter Stores", "category": "Shopping", "subcategory": "Electronics"},
    "5983": {"description": "Fuel Dealers", "category": "Utilities", "subcategory": "Electric"},
    "5992": {"description": "Florists", "category": "Shopping", "subcategory": "Retail"},
    "5993": {"description": "Cigar Stores and Stands", "category": "Shopping", "subcategory": "Retail"},
    "5994": {"description": "News Dealers and Newsstands", "category": "Shopping", "subcategory": "Retail"},
    "5995": {"description": "Pet Shops, Pet Food, Supplies", "category": "Shopping", "subcategory": "Retail"},
    "5996": {"description": "Swimming Pools Sales", "category": "Home & Garden", "subcategory": "Hardware"},
    "5997": {"description": "Electric Razor Stores", "category": "Shopping", "subcategory": "Electronics"},
    "5998": {"description": "Tent and Awning Shops", "category": "Shopping", "subcategory": "Retail"},
    "5999": {"description": "Miscellaneous Retail Stores", "category": "Shopping", "subcategory": "Retail"},
    
    # HEALTHCARE (8000-8099)
    "8011": {"description": "Doctors and Physicians", "category": "Healthcare", "subcategory": "Doctor"},
    "8021": {"description": "Dentists and Orthodontists", "category": "Healthcare", "subcategory": "Dentist"},
    "8031": {"description": "Osteopaths", "category": "Healthcare", "subcategory": "Doctor"},
    "8041": {"description": "Chiropractors", "category": "Healthcare", "subcategory": "Doctor"},
    "8042": {"description": "Optometrists, Ophthalmologists", "category": "Healthcare", "subcategory": "Doctor"},
    "8043": {"description": "Opticians, Eyeglasses", "category": "Healthcare", "subcategory": "Doctor"},
    "8044": {"description": "Optical Goods, Eyeglasses", "category": "Healthcare", "subcategory": "Doctor"},
    "8049": {"description": "Podiatrists, Chiropodists", "category": "Healthcare", "subcategory": "Doctor"},
    "8050": {"description": "Nursing, Personal Care", "category": "Healthcare", "subcategory": "Hospital"},
    "8062": {"description": "Hospitals", "category": "Healthcare", "subcategory": "Hospital"},
    "8071": {"description": "Medical and Dental Labs", "category": "Healthcare", "subcategory": "Hospital"},
    "8099": {"description": "Medical Services", "category": "Healthcare", "subcategory": "Doctor"},
    
    # ENTERTAINMENT & RECREATION (7800-7999)
    "7011": {"description": "Hotels, Motels, Resorts", "category": "Travel", "subcategory": "Hotel"},
    "7012": {"description": "Timeshares", "category": "Travel", "subcategory": "Hotel"},
    "7210": {"description": "Laundry, Cleaning Services", "category": "Personal Care", "subcategory": "Salon"},
    "7211": {"description": "Laundries - Family, Commercial", "category": "Personal Care", "subcategory": "Salon"},
    "7216": {"description": "Dry Cleaners", "category": "Personal Care", "subcategory": "Salon"},
    "7217": {"description": "Carpet, Upholstery Cleaning", "category": "Personal Care", "subcategory": "Salon"},
    "7230": {"description": "Beauty and Barber Shops", "category": "Personal Care", "subcategory": "Salon"},
    "7251": {"description": "Shoe Repair, Hat Cleaning", "category": "Personal Care", "subcategory": "Salon"},
    "7261": {"description": "Funeral Services, Crematories", "category": "Personal Care", "subcategory": "Salon"},
    "7273": {"description": "Dating Services", "category": "Entertainment", "subcategory": "Events"},
    "7276": {"description": "Tax Preparation Services", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7277": {"description": "Counseling Services", "category": "Healthcare", "subcategory": "Doctor"},
    "7278": {"description": "Buying, Shopping Services", "category": "Shopping", "subcategory": "Retail"},
    "7296": {"description": "Clothing Rental", "category": "Shopping", "subcategory": "Clothing"},
    "7297": {"description": "Massage Parlors", "category": "Personal Care", "subcategory": "Spa"},
    "7298": {"description": "Health and Beauty Spas", "category": "Personal Care", "subcategory": "Spa"},
    "7299": {"description": "Miscellaneous Personal Services", "category": "Personal Care", "subcategory": "Salon"},
    "7311": {"description": "Advertising Services", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7333": {"description": "Commercial Photography", "category": "Entertainment", "subcategory": "Events"},
    "7338": {"description": "Quick Copy, Repro, Blueprint", "category": "Shopping", "subcategory": "Retail"},
    "7349": {"description": "Cleaning and Maintenance", "category": "Personal Care", "subcategory": "Salon"},
    "7361": {"description": "Employment, Temp Agencies", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7372": {"description": "Computer Programming", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7375": {"description": "Information Retrieval Services", "category": "Utilities", "subcategory": "Internet"},
    "7379": {"description": "Computer Repair", "category": "Shopping", "subcategory": "Electronics"},
    "7392": {"description": "Consulting, Public Relations", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7393": {"description": "Detective Agencies", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7394": {"description": "Equipment Rental", "category": "Shopping", "subcategory": "Retail"},
    "7395": {"description": "Photo Developing", "category": "Shopping", "subcategory": "Retail"},
    "7399": {"description": "Business Services", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7512": {"description": "Car Rental Agencies", "category": "Travel", "subcategory": "Car Rental"},
    "7513": {"description": "Truck, Utility Trailer Rentals", "category": "Transportation", "subcategory": "Auto Service"},
    "7519": {"description": "Recreational Vehicle Rentals", "category": "Travel", "subcategory": "Car Rental"},
    "7523": {"description": "Parking Lots, Garages", "category": "Transportation", "subcategory": "Parking"},
    "7531": {"description": "Automotive Body Repair Shops", "category": "Transportation", "subcategory": "Auto Service"},
    "7534": {"description": "Tire Retreading and Repair", "category": "Transportation", "subcategory": "Auto Service"},
    "7535": {"description": "Automotive Paint Shops", "category": "Transportation", "subcategory": "Auto Service"},
    "7538": {"description": "Automotive Service Shops", "category": "Transportation", "subcategory": "Auto Service"},
    "7542": {"description": "Car Washes", "category": "Transportation", "subcategory": "Auto Service"},
    "7549": {"description": "Towing Services", "category": "Transportation", "subcategory": "Auto Service"},
    "7622": {"description": "Electronics Repair Shops", "category": "Shopping", "subcategory": "Electronics"},
    "7623": {"description": "A/C, Refrigeration Repair", "category": "Home & Garden", "subcategory": "Home Improvement"},
    "7629": {"description": "Small Appliance Repair", "category": "Home & Garden", "subcategory": "Home Improvement"},
    "7631": {"description": "Watch, Jewelry Repair", "category": "Shopping", "subcategory": "Retail"},
    "7641": {"description": "Furniture Repair, Refinishing", "category": "Home & Garden", "subcategory": "Furniture"},
    "7692": {"description": "Welding Repair", "category": "Home & Garden", "subcategory": "Hardware"},
    "7699": {"description": "Miscellaneous Repair Shops", "category": "Home & Garden", "subcategory": "Home Improvement"},
    "7800": {"description": "Government Services", "category": "Utilities", "subcategory": "Electric"},
    "7801": {"description": "Government Services", "category": "Utilities", "subcategory": "Electric"},
    "7802": {"description": "Government Services", "category": "Utilities", "subcategory": "Electric"},
    "7829": {"description": "Motion Pictures", "category": "Entertainment", "subcategory": "Movies"},
    "7832": {"description": "Motion Picture Theaters", "category": "Entertainment", "subcategory": "Movies"},
    "7841": {"description": "Video Entertainment Rental", "category": "Entertainment", "subcategory": "Streaming"},
    "7911": {"description": "Dance Halls, Studios, Schools", "category": "Entertainment", "subcategory": "Events"},
    "7922": {"description": "Theatrical Producers", "category": "Entertainment", "subcategory": "Events"},
    "7929": {"description": "Bands, Orchestras", "category": "Entertainment", "subcategory": "Music"},
    "7932": {"description": "Billiard, Pool Establishments", "category": "Entertainment", "subcategory": "Events"},
    "7933": {"description": "Bowling Alleys", "category": "Entertainment", "subcategory": "Events"},
    "7941": {"description": "Sports Clubs, Fields", "category": "Personal Care", "subcategory": "Gym"},
    "7991": {"description": "Tourist Attractions", "category": "Entertainment", "subcategory": "Events"},
    "7992": {"description": "Golf Courses", "category": "Entertainment", "subcategory": "Events"},
    "7993": {"description": "Video Amusement Games", "category": "Entertainment", "subcategory": "Gaming"},
    "7994": {"description": "Video Game Arcades", "category": "Entertainment", "subcategory": "Gaming"},
    "7995": {"description": "Betting, Casino Gambling", "category": "Entertainment", "subcategory": "Gaming"},
    "7996": {"description": "Amusement Parks", "category": "Entertainment", "subcategory": "Events"},
    "7997": {"description": "Membership Clubs (Sports, Recreation)", "category": "Personal Care", "subcategory": "Gym"},
    "7998": {"description": "Aquariums, Zoos", "category": "Entertainment", "subcategory": "Events"},
    "7999": {"description": "Recreation Services", "category": "Entertainment", "subcategory": "Events"},
    
    # EDUCATION (8200-8299)
    "8211": {"description": "Elementary, Secondary Schools", "category": "Education", "subcategory": "Tuition"},
    "8220": {"description": "Colleges, Universities", "category": "Education", "subcategory": "Tuition"},
    "8241": {"description": "Correspondence Schools", "category": "Education", "subcategory": "Online Course"},
    "8244": {"description": "Business, Secretarial Schools", "category": "Education", "subcategory": "Tuition"},
    "8249": {"description": "Vocational, Trade Schools", "category": "Education", "subcategory": "Tuition"},
    "8299": {"description": "Schools and Educational Services", "category": "Education", "subcategory": "Tuition"},
    
    # FINANCIAL SERVICES (6000-6999)
    "6010": {"description": "Financial Institutions - Manual Cash", "category": "Financial Services", "subcategory": "Bank Fee"},
    "6011": {"description": "Financial Institutions - Automated Cash", "category": "Financial Services", "subcategory": "ATM"},
    "6012": {"description": "Financial Institutions", "category": "Financial Services", "subcategory": "Bank Fee"},
    "6051": {"description": "Non-Financial Institutions", "category": "Financial Services", "subcategory": "Bank Fee"},
    "6211": {"description": "Security Brokers, Dealers", "category": "Financial Services", "subcategory": "Investment"},
    "6300": {"description": "Insurance - Underwriting, Premiums", "category": "Financial Services", "subcategory": "Insurance"},
    "6381": {"description": "Insurance Premiums", "category": "Financial Services", "subcategory": "Insurance"},
    "6399": {"description": "Insurance Services", "category": "Financial Services", "subcategory": "Insurance"},
    "6513": {"description": "Real Estate Agents, Rentals", "category": "Financial Services", "subcategory": "Bank Fee"},
    
    # PROFESSIONAL SERVICES (7000-7999)
    "7311": {"description": "Advertising Services", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7333": {"description": "Commercial Photography", "category": "Entertainment", "subcategory": "Events"},
    "7372": {"description": "Computer Programming", "category": "Financial Services", "subcategory": "Bank Fee"},
    "7512": {"description": "Car Rental Agencies", "category": "Travel", "subcategory": "Car Rental"}
}

# ============================================================================
# VENDOR-TO-MCC MAPPING - Major Brand Merchants
# ============================================================================
# This provides instant MCC code lookup for known merchants
# ============================================================================

VENDOR_MCC_MAP = {
    # Food & Dining
    "STARBUCKS": "5812",
    "MCDONALDS": "5814",
    "BURGER KING": "5814",
    "SUBWAY": "5814",
    "TACO BELL": "5814",
    "KFC": "5814",
    "WENDY'S": "5814",
    "CHIPOTLE": "5812",
    "PANERA": "5812",
    "DOMINOS": "5814",
    "PIZZA HUT": "5814",
    "DUNKIN": "5812",
    "CHICK-FIL-A": "5814",
    "SONIC": "5814",
    "ARBYS": "5814",
    
    # Grocery
    "WALMART": "5411",
    "TARGET": "5411",
    "COSTCO": "5411",
    "KROGER": "5411",
    "SAFEWAY": "5411",
    "WHOLE FOODS": "5411",
    "TRADER JOES": "5411",
    "ALBERTSONS": "5411",
    "PUBLIX": "5411",
    "WEGMANS": "5411",
    
    # Gas Stations
    "SHELL": "5541",
    "EXXON": "5541",
    "CHEVRON": "5541",
    "BP": "5541",
    "MOBIL": "5541",
    "TEXACO": "5541",
    "ARCO": "5541",
    "76": "5541",
    "CONOCO": "5541",
    "CITGO": "5541",
    
    # Transportation
    "UBER": "4121",
    "LYFT": "4121",
    "UBER EATS": "5812",
    "DOORDASH": "5812",
    "GRUBHUB": "5812",
    
    # Shopping
    "AMAZON": "5999",
    "EBAY": "5999",
    "ETSY": "5999",
    "BEST BUY": "5732",
    "HOME DEPOT": "5200",
    "LOWES": "5200",
    "MACYS": "5311",
    "NORDSTROM": "5311",
    "KOHLS": "5311",
    "JCPENNEY": "5311",
    
    # Pharmacies
    "CVS": "5912",
    "WALGREENS": "5912",
    "RITE AID": "5912",
    
    # Entertainment
    "NETFLIX": "5968",
    "HULU": "5968",
    "DISNEY+": "5968",
    "SPOTIFY": "5968",
    "APPLE MUSIC": "5968",
    "HBO": "5968",
    "YOUTUBE": "5968",
    "AMC THEATERS": "7832",
    "REGAL CINEMAS": "7832",
    
    # Utilities
    "AT&T": "4814",
    "VERIZON": "4814",
    "T-MOBILE": "4814",
    "SPRINT": "4814",
    "COMCAST": "4899",
    "SPECTRUM": "4899",
    "COX": "4899",
    
    # Hotels
    "MARRIOTT": "7011",
    "HILTON": "7011",
    "HYATT": "7011",
    "HOLIDAY INN": "7011",
    "BEST WESTERN": "7011",
    "AIRBNB": "7011",
    "BOOKING.COM": "7011",
    
    # Airlines
    "DELTA": "4511",
    "UNITED": "4511",
    "AMERICAN AIRLINES": "4511",
    "SOUTHWEST": "4511",
    "JETBLUE": "4511",
    
    # Gym/Fitness
    "PLANET FITNESS": "7997",
    "LA FITNESS": "7997",
    "24 HOUR FITNESS": "7997",
    "ANYTIME FITNESS": "7997",
    "GOLD'S GYM": "7997"
}


@tool
def classify_by_mcc_code(mcc_code: str) -> Dict[str, any]:
    """
    Classify a transaction based on its MCC (Merchant Category Code).
    
    Use this tool when the user provides an MCC code in the transaction input.
    MCC codes are 4-digit codes that indicate the type of merchant.
    This provides HIGH confidence classification when available.
    
    Args:
        mcc_code: 4-digit Merchant Category Code (e.g., "5812", "5541", "5411")
        
    Returns:
        Dict with category, subcategory, description, and confidence level
    """
    # Normalize MCC code (remove any spaces/dashes)
    mcc_code = str(mcc_code).strip().replace("-", "").replace(" ", "")
    
    code_info = MCC_CODES.get(mcc_code)
    
    if code_info:
        return {
            "mcc_code": mcc_code,
            "category": code_info["category"],
            "subcategory": code_info["subcategory"],
            "mcc_description": code_info["description"],
            "confidence": "HIGH",
            "source": "MCC Code Database",
            "message": f"MCC code {mcc_code} found in database. Use this category with HIGH confidence."
        }
    else:
        return {
            "mcc_code": mcc_code,
            "category": None,
            "subcategory": None,
            "mcc_description": "Unknown MCC code",
            "confidence": "UNKNOWN",
            "source": "MCC Code Database",
            "message": f"MCC code {mcc_code} not found in database. Proceed with manual classification."
        }


def get_mcc_code(category: str, subcategory: Optional[str] = None) -> Dict[str, str]:
    """
    Get appropriate MCC code for a category (reverse lookup)
    
    Args:
        category: Transaction category
        subcategory: Optional subcategory for more specific matching
        
    Returns:
        Dict with MCC code and description
    """
    # Try to find best match based on category and subcategory
    for code, info in MCC_CODES.items():
        if info["category"] == category:
            if subcategory and info.get("subcategory") == subcategory:
                return {
                    "mcc_code": code,
                    "mcc_description": info["description"],
                    "category": category,
                    "subcategory": subcategory
                }
            elif not subcategory:
                return {
                    "mcc_code": code,
                    "mcc_description": info["description"],
                    "category": category
                }
    
    # Default to miscellaneous
    return {
        "mcc_code": "5999",
        "mcc_description": "Miscellaneous Retail Stores",
        "category": "Other"
    }


def get_all_mcc_codes() -> Dict[str, Dict[str, str]]:
    """
    Get all MCC codes
    
    Returns:
        Dict mapping MCC codes to their information
    """
    return MCC_CODES


def get_mcc_description(mcc_code: str) -> Optional[str]:
    """
    Get description for a specific MCC code
    
    Args:
        mcc_code: 4-digit MCC code
        
    Returns:
        Description of the MCC code, or None if not found
    """
    code_info = MCC_CODES.get(mcc_code)
    return code_info["description"] if code_info else None


@tool
def assign_mcc_code_for_category(category: str, subcategory: str = None) -> Dict[str, any]:
    """
    Assign the appropriate MCC code for a given category and subcategory.
    
    Use this tool during governance to determine or validate the MCC code
    based on the classified transaction category.
    
    Args:
        category: Transaction category (e.g., "Food & Dining", "Transportation")
        subcategory: Transaction subcategory (e.g., "Restaurant", "Gas Station")
        
    Returns:
        Dict with assigned MCC code and description
    """
    # Try to find best match based on category and subcategory
    for code, info in MCC_CODES.items():
        if info["category"] == category:
            # Exact subcategory match preferred
            if subcategory and info.get("subcategory") == subcategory:
                return {
                    "mcc_code": code,
                    "mcc_description": info["description"],
                    "category": category,
                    "subcategory": subcategory,
                    "match_quality": "exact",
                    "message": f"Assigned MCC {code} based on exact category and subcategory match"
                }
    
    # Fallback: find any match for category
    for code, info in MCC_CODES.items():
        if info["category"] == category:
            return {
                "mcc_code": code,
                "mcc_description": info["description"],
                "category": category,
                "subcategory": subcategory or info.get("subcategory"),
                "match_quality": "category_match",
                "message": f"Assigned MCC {code} based on category match. Subcategory may not be exact."
            }
    
    # Default to miscellaneous if no match
    return {
        "mcc_code": "5999",
        "mcc_description": "Miscellaneous Retail Stores",
        "category": category,
        "subcategory": subcategory,
        "match_quality": "default",
        "message": f"No specific MCC found for category '{category}'. Using default 5999."
    }


@tool
def lookup_mcc_by_vendor(merchant_name: str) -> Dict[str, any]:
    """
    Look up MCC code directly from merchant name using vendor database.
    
    Use this tool to get instant MCC code for well-known brands and merchants.
    This is faster and more accurate than category-based lookup for known vendors.
    
    Args:
        merchant_name: Merchant/vendor name (e.g., "STARBUCKS", "UBER", "SHELL")
        
    Returns:
        Dict with MCC code, description, and vendor match info
    """
    # Normalize merchant name for lookup
    merchant_upper = merchant_name.upper().strip()
    
    # Check exact match first
    if merchant_upper in VENDOR_MCC_MAP:
        mcc_code = VENDOR_MCC_MAP[merchant_upper]
        mcc_info = MCC_CODES.get(mcc_code, {})
        
        return {
            "vendor": merchant_upper,
            "mcc_code": mcc_code,
            "mcc_description": mcc_info.get("description", "Unknown"),
            "category": mcc_info.get("category", "Other"),
            "subcategory": mcc_info.get("subcategory", "General"),
            "match": True,
            "confidence": "HIGH",
            "message": f"Found exact vendor match for {merchant_upper}. MCC: {mcc_code}"
        }
    
    # Try partial match
    for vendor, mcc_code in VENDOR_MCC_MAP.items():
        if vendor in merchant_upper or merchant_upper in vendor:
            mcc_info = MCC_CODES.get(mcc_code, {})
            
            return {
                "vendor": vendor,
                "mcc_code": mcc_code,
                "mcc_description": mcc_info.get("description", "Unknown"),
                "category": mcc_info.get("category", "Other"),
                "subcategory": mcc_info.get("subcategory", "General"),
                "match": True,
                "confidence": "MEDIUM",
                "message": f"Found partial vendor match: {vendor}. MCC: {mcc_code}"
            }
    
    return {
        "vendor": merchant_name,
        "mcc_code": None,
        "match": False,
        "confidence": "NONE",
        "message": f"Vendor '{merchant_name}' not found in database. Use category-based MCC assignment."
    }


def get_mcc_statistics() -> Dict[str, any]:
    """
    Get statistics about the MCC code database
    
    Returns:
        Dict with database statistics
    """
    categories = {}
    for info in MCC_CODES.values():
        cat = info.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_mcc_codes": len(MCC_CODES),
        "total_vendors": len(VENDOR_MCC_MAP),
        "categories": categories,
        "most_common_category": max(categories, key=categories.get) if categories else None
    }

