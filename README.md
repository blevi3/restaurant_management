# MyRestaurant Web Application

## Introduction

MyRestaurant is a comprehensive web application built with Python and the Django framework, designed to provide a modern online experience for restaurant customers and efficient management tools for staff. It features online ordering, table reservations, payment processing, and an administrative dashboard.

## Key Features

This application boasts a range of features for both customers and administrators:

* **Online Ordering:** Customers can browse the menu (foods and drinks), customize items with extras, add comments, and place orders through an intuitive interface.
* **Shopping Cart:** A fully functional shopping cart system allows users to add/remove items, adjust quantities, and apply coupons before checkout.
* **Table Reservations:** Users can check table availability for specific dates and times, and book tables online.
* **QR Code Integration:** Table-specific QR codes can be scanned by customers to easily access the menu and ordering system, linking their order to their table.
* **User Authentication:** Secure user registration, login, password reset functionality, and Google Social Login integration using Django `allauth`.
* **Payment Processing:** Secure online payments integrated via Stripe, including handling checkout sessions and webhook events for payment confirmation.
* **Coupon System:** Supports various coupon types (fixed amount, percentage), product-specific discounts, unique codes, and a points-based redemption system.
* **User Profiles:** Users have profiles storing their details, points earned from orders, and acquired coupons.
* **Order Management (Staff):** Staff can view all incoming orders (paid and unpaid) and mark them as delivered or paid.
* **Reservation Management (Staff):** Staff can view all current and past reservations and mark them as 'taken' when customers arrive.
* **Admin Dashboard:** A dashboard provides insights into total sales, popular items, reservation statistics, top customers, user activity, and server status.
* **Item Recommendations:** Suggests menu items to users based on historical order data.
* **Ingredient & Extra Management:** Allows administrators to manage menu item ingredients and add customizable extras with associated costs.
* **PDF Receipts:** Automatically generates PDF receipts upon successful payment and emails them to the customer.
* **Multi-language Support:** The interface supports multiple languages, managed through user profiles.
* **Location-Based Access:** Middleware restricts access to certain features (like QR scanning) based on user's geographical location.

## Technology Stack

* **Backend:** Python, Django
* **Database:** Django ORM (compatible with PostgreSQL, MySQL, SQLite)
* **Frontend:** HTML, CSS, JavaScript
* **JavaScript Libraries:** jQuery, Leaflet (for maps), Chart.js (for dashboard), Galleria (for gallery)
* **CSS Frameworks:** Bootstrap
* **Payment Gateway:** Stripe API
* **PDF Generation:** ReportLab
* **Authentication:** Django `allauth`
* **Other Libraries:** `psutil`, `matplotlib`, `geopy`


## Installation

1.  Clone the repository: `git clone ...`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4.  Install dependencies: `pip install -r requirements.txt` (You'll need to create this file)
5.  Configure environment variables (e.g., `SECRET_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, database settings).
6.  Run migrations: `python manage.py migrate`
7.  Run the development server: `python manage.py runserver`

