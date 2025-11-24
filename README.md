# Ub'EJR Eats - Setup and use guide

## I. Installation

1. **Start Onyxia services**
This application can only be used in Onyxia and some services are needed.

    - Create a VSCode session and make sure to forward the port **8000** while creating it
    - Create a Postgresql session

2. **Clone the project**:

```bash
git clone https://github.com/WandrilleDorchies/Projet2A_UbEJR.git
cd Projet2A_UbEJR
```

3. **Install dependencies** :

```bash
pip install --user pdm uv
pdm install
```

This will setup all we need for this project to work:
- A virtual environnment
- Install all packages in their right version

**All the files for the application are now downloaded**

## II. Configuration

Create `.env` file at the root of the project. It should have the following variables

```env
# PostgreSQL Configuration 
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=defaultdb
POSTGRES_USER=<your postgre username>
POSTGRES_PASSWORD=<you postgre password>
POSTGRES_SCHEMA=project
POSTGRES_SCHEMA_TEST=test

# JWT
JWT_SECRET=<a newly generated JWT token>

# Google Maps API
GOOGLE_MAPS_API_KEY=<your google maps api key>

# Stripe
STRIPE_SECRET_KEY=<your stripe api key>
BASE_URL=<your onyxia url>
```
The variables related to postgre can be found in the README of your Postgresql service.

The base url can be found when you launch an onyxia service. It's usually something like :
```
user-<username>-<some numbers>.user.lab.sspcloud.fr/
```
The backlash is very important, don't forget to include it


## III. Initialise the database

### 1. Reset the database for production

You can easily populate the database with a working example. It contains a single user, a driver and an admin. There is also some items and bundles along with their images. All you have to do is :

```bash
pdm resetprod
```

### 2. Reset the database for scalability test

But you can also populate the database with mock data created with the package `faker`. It inserts fake users, drivers and admins but also orderables and orders to see if the application can support a large amount of users.

```bash
pdm resetscale
```

## IV. Launching the app

### 1. Starting the server

Start the uvicorn server with this simple command :

```bash
pdm start
```

### 2. Opening the web-interface

1. Now go back to services selection page of Onyxia. 
2. Click on the **Open** button of VSCode.
3. If you've correctly forwarded the port **8000** you should see a **port 8000** button.
4. Simply press it and you will be redirected to the login page.

### V. Tests

You can launch the tests with this command: 

```bash
pdm test
```

Note that the tests related to JWT won't be working since you generated a different secret
