# DeviceZone E-Commerce Store

This is an online store for purchasing computer devices. It offers a modern UI and seamless payment integration with Stripe.

## Installation and Setup

### Prerequisites
Ensure you have Docker and Docker Compose installed.

### Running the Project

1. Clone the repository:

```sh
git clone <repository-url>
cd DjangoProjectShop
```

2. Build and start the containers:

```sh
docker compose up --build -d
```

3. Create a superuser for the admin panel:

```sh
docker exec -it my-app-container python manage.py createsuperuser
```

4. Open your browser and go to `http://127.0.0.1:8000/` to access the store.

## Technology Stack

- **Frontend:** jQuery, TailwindCSS, HTML
- **Backend:** Python, Django, Celery, Pytest
- **CICD:** Docker/Docker Compose, GitHub Actions
- **Payments:** Stripe

## Images: 

### index 
![index](images/index.png)
### login 
![login](images/login.png)
### catalog 
![catalog](images/catalog.png)
### detail 
![detail](images/detail.png)
### cart 
![cart](images/cart.png)
### checkout 
![checkout](images/checkout.png)
### payment 
![payment](images/payment.png)
