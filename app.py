import flet as ft
import requests
from pie_chart import plot_reviews_chart

API_URL = "http://localhost:8000"

# ------------------ API Calls (BACKEND UNCHANGED) ------------------

def login_api(username, password):
    r = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
    return r.json() if r.status_code == 200 else None

def signup_api(username, password):
    r = requests.post(f"{API_URL}/auth/signup", json={"username": username, "password": password})
    return r.status_code == 200

def fetch_recipes():
    r = requests.get(f"{API_URL}/jobs/")
    return r.json() if r.status_code == 200 else []

def fetch_reviews(recipe_id):
    r = requests.get(f"{API_URL}/reviews/{recipe_id}")
    return r.json() if r.status_code == 200 else []

def fetch_average_rating(recipe_id):
    r = requests.get(f"{API_URL}/jobs/{recipe_id}/rating")
    return r.json().get("average_rating", "N/A") if r.status_code == 200 else "N/A"

def add_recipe_api(name, description):
    return requests.post(f"{API_URL}/jobs/", json={"name": name, "description": description})

def edit_recipe_api(recipe_id, name, description):
    return requests.put(
        f"{API_URL}/jobs/{recipe_id}",
        json={"name": name, "description": description},
    )

def delete_recipe_api(recipe_id):
    return requests.delete(f"{API_URL}/jobs/{recipe_id}")

def submit_review_api(recipe_id, username, rating, text):
    return requests.post(
        f"{API_URL}/reviews/{recipe_id}",
        json={"username": username, "rating": rating, "text": text},
    )

# ------------------ AUTH PAGES ------------------

def login_page(page):
    page.controls.clear()
    page.title = "CookQuest 🍳"

    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    message = ft.Text("", color="red")

    def handle_login(e):
        user = login_api(username.value, password.value)
        if user:
            if user["role"] == "admin":
                admin_dashboard(page)
            else:
                customer_page(page, user["username"])
        else:
            message.value = "Invalid credentials"
            page.update()

    page.controls.extend([
        ft.Text("Login", size=24),
        username,
        password,
        ft.ElevatedButton("Login", on_click=handle_login),
        ft.ElevatedButton("Sign Up", on_click=lambda e: signup_page(page)),
        message,
    ])
    page.update()

def signup_page(page):
    page.controls.clear()
    page.title = "Sign Up"

    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    confirm = ft.TextField(label="Confirm Password", password=True)
    message = ft.Text("", color="red")

    def handle_signup(e):
        if password.value != confirm.value:
            message.value = "Passwords do not match"
            page.update()
            return
        if signup_api(username.value, password.value):
            login_page(page)
        else:
            message.value = "Username already exists"
            page.update()

    page.controls.extend([
        ft.Text("Create Account", size=24),
        username,
        password,
        confirm,
        ft.ElevatedButton("Sign Up", on_click=handle_signup),
        ft.ElevatedButton("Back", on_click=lambda e: login_page(page)),
        message,
    ])
    page.update()

def logout_button(page):
    return ft.ElevatedButton("Logout", on_click=lambda e: login_page(page))

# ------------------ ADMIN ------------------

def admin_dashboard(page):
    page.controls.clear()
    page.controls.append(ft.Text("Admin Panel", size=26))
    page.controls.append(logout_button(page))

    name = ft.TextField(label="Recipe Name")
    desc = ft.TextField(label="Recipe Description", multiline=True)

    def add_recipe(e):
        if name.value and desc.value:
            add_recipe_api(name.value, desc.value)
            admin_dashboard(page)

    search = ft.TextField(label="Search Recipes")
    recipe_list = ft.ListView(expand=True)

    def refresh():
        recipe_list.controls.clear()
        for recipe in fetch_recipes():
            if search.value.lower() in recipe["name"].lower():
                recipe_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(recipe["name"]),
                        subtitle=ft.Text(recipe["description"]),
                        on_click=lambda e, r=recipe: edit_recipe_page(page, r),
                    )
                )
        page.update()

    search.on_change = lambda e: refresh()
    refresh()

    page.controls.extend([
        name,
        desc,
        ft.ElevatedButton("Add Recipe", on_click=add_recipe),
        search,
        recipe_list,
    ])
    page.update()

def edit_recipe_page(page, recipe):
    page.controls.clear()
    page.controls.append(logout_button(page))

    name = ft.TextField(label="Recipe Name", value=recipe["name"])
    desc = ft.TextField(label="Recipe Description", value=recipe["description"], multiline=True)

    page.controls.extend([
        ft.Text(f"Edit Recipe: {recipe['name']}", size=22),
        name,
        desc,
        ft.ElevatedButton(
            "Save Changes",
            on_click=lambda e: (
                edit_recipe_api(recipe["_id"], name.value, desc.value),
                admin_dashboard(page),
            ),
        ),
        ft.ElevatedButton(
            "Delete Recipe",
            on_click=lambda e: (
                delete_recipe_api(recipe["_id"]),
                admin_dashboard(page),
            ),
        ),
    ])
    page.update()

# ------------------ CUSTOMER ------------------

def customer_page(page, username):
    page.controls.clear()
    page.controls.append(ft.Text(f"Welcome, {username} 👋", size=26))
    page.controls.append(logout_button(page))

    search = ft.TextField(label="Search Recipes")
    recipe_list = ft.ListView(expand=True)

    def refresh():
        recipe_list.controls.clear()
        for recipe in fetch_recipes():
            if search.value.lower() in recipe["name"].lower():
                recipe_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(recipe["name"]),
                        subtitle=ft.Text(recipe["description"]),
                        on_click=lambda e, r=recipe: recipe_details(page, r, username),
                    )
                )
        page.update()

    search.on_change = lambda e: refresh()
    refresh()

    page.controls.extend([search, recipe_list])
    page.update()

def recipe_details(page, recipe, username):
    page.controls.clear()
    page.controls.append(logout_button(page))

    avg = fetch_average_rating(recipe["_id"])

    page.controls.extend([
        ft.Text(recipe["name"], size=24),
        ft.Text(recipe["description"]),
        ft.Text(f"Average Rating: ⭐ {avg}"),
    ])

    for review in fetch_reviews(recipe["_id"]):
        page.controls.append(
            ft.Text(f"{review['username']} ⭐ {review['rating']} — {review['text']}")
        )

    rating = ft.Slider(min=1, max=5, divisions=4, value=3)
    text = ft.TextField(label="Write a review", multiline=True)

    page.controls.extend([
        rating,
        text,
        ft.ElevatedButton(
            "Submit Review",
            on_click=lambda e: (
                submit_review_api(recipe["_id"], username, int(rating.value), text.value),
                recipe_details(page, recipe, username),
            ),
        ),
        ft.ElevatedButton(
            "View Rating Chart",
            on_click=lambda e: plot_reviews_chart(recipe["_id"]),
        ),
        ft.ElevatedButton(
            "Back",
            on_click=lambda e: customer_page(page, username),
        ),
    ])
    page.update()

# ------------------ APP START ------------------

def main(page: ft.Page):
    login_page(page)

ft.app(target=main)
