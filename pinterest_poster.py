#!/usr/bin/env python3
"""
Pinterest Auto-Poster for MyWeekDayBirth
Posts pins via Pinterest API v5
Runs via Claude scheduled task 3x/day

Usage:
  PINTEREST_TOKEN=xxx python3 pinterest_poster.py
"""

import os
import json
import time
import random
import requests
from datetime import datetime, date

# ─── Config ───────────────────────────────────────────────────────────────────
PINTEREST_TOKEN = os.environ.get("PINTEREST_TOKEN", "")
BASE_URL = "https://api.pinterest.com/v5"
SHOP_URL = "https://myweekdaybirth.com/products/"

HEADERS = {
    "Authorization": f"Bearer {PINTEREST_TOKEN}",
    "Content-Type": "application/json",
}

# Board names to create/use (keyword-optimized)
BOARDS = {
    "baby_shower_gifts":    "Baby Shower Gift Ideas 🎁",
    "personalized_baby":    "Personalized Newborn Gifts",
    "monday_babies":        "Monday Baby Gifts 🌙",
    "tuesday_babies":       "Tuesday Baby Gifts ✨",
    "wednesday_babies":     "Wednesday Baby Gifts 🌿",
    "thursday_babies":      "Thursday Baby Gifts ⚡",
    "friday_babies":        "Friday Baby Gifts 🌟",
    "saturday_babies":      "Saturday Baby Gifts ☀️",
    "sunday_babies":        "Sunday Baby Gifts 💜",
}

# ─── Product data with Shopify CDN URLs ───────────────────────────────────────
PRODUCTS = [
    {"day": "Monday",    "slogan": "Still Figuring Out Sleep",              "handle": "personalized-baby-pajama-born-on-monday-still-figuring-out-sleep",              "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-short-sleeve-bodysuit-heather-front-6a39072ec70b8.jpg"},
    {"day": "Monday",    "slogan": "Ignores Bedtime",                       "handle": "personalized-baby-pajama-born-on-monday-ignores-bedtime",                       "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-ash-front-6a39063e9384d.jpg"},
    {"day": "Monday",    "slogan": "Running on Lunar Time",                 "handle": "personalized-baby-pajama-born-on-monday-running-on-lunar-time",                 "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-ash-front-6a3908b428f4f.jpg"},
    {"day": "Tuesday",   "slogan": "Born to Blaze",                        "handle": "personalized-baby-pajama-born-on-tuesday-born-to-blaze",                        "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-ash-front-6a39523bd7383.jpg"},
    {"day": "Tuesday",   "slogan": "Passionate Since Minute One",           "handle": "personalized-baby-pajama-born-on-tuesday-passionate-since-minute-one",          "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a395608d8736.jpg"},
    {"day": "Tuesday",   "slogan": "Too Bright to Be Contained",            "handle": "personalized-baby-pajama-born-on-tuesday-too-bright-to-be-contained",           "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-ash-front-6a39569662a06.jpg"},
    {"day": "Wednesday", "slogan": "Chaos Coordinator",                     "handle": "personalized-baby-pajama-born-on-wednesday-chaos-coordinator",                  "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a39573430b90.jpg"},
    {"day": "Wednesday", "slogan": "Arrived Unexpectedly",                  "handle": "personalized-baby-pajama-born-on-wednesday-arrived-unexpectedly",               "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a39573430b90.jpg"},
    {"day": "Wednesday", "slogan": "Midweek Magic",                         "handle": "personalized-baby-pajama-born-on-wednesday-midweek-magic",                      "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-vintage-indigo-front-6a395d2768c08.jpg"},
    {"day": "Thursday",  "slogan": "Born With an Agenda",                   "handle": "personalized-baby-pajama-born-on-thursday-born-with-an-agenda",                 "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a395ee7313a5.jpg"},
    {"day": "Thursday",  "slogan": "Future Boss",                           "handle": "personalized-baby-pajama-born-on-thursday-future-boss",                         "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-vintage-indigo-front-6a395ffa6c9cd.jpg"},
    {"day": "Thursday",  "slogan": "Little Thunder",                        "handle": "personalized-baby-pajama-born-on-thursday-little-thunder",                      "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-black-front-6a396073a0c72.jpg"},
    {"day": "Friday",    "slogan": "Joy and Beauty",                        "handle": "personalized-baby-pajama-born-on-friday-joy-and-beauty",                        "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-vintage-indigo-front-6a39611e8b197.jpg"},
    {"day": "Friday",    "slogan": "Little Party Starter",                  "handle": "personalized-baby-pajama-born-on-friday-little-party-starter",                  "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-ash-front-6a3961b0ea8cf.jpg"},
    {"day": "Friday",    "slogan": "Best Thing to Happen on a Friday",      "handle": "personalized-baby-pajama-born-on-friday-best-thing-to-happen-on-a-friday",      "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a39621f235e9.jpg"},
    {"day": "Saturday",  "slogan": "Little Sunshine",                       "handle": "personalized-baby-pajama-born-on-saturday-little-sunshine",                     "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-black-front-6a3962c3bbcf4.jpg"},
    {"day": "Saturday",  "slogan": "Allergic to Schedules",                 "handle": "personalized-baby-pajama-born-on-saturday-allergic-to-schedules",               "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a39634011ca6.jpg"},
    {"day": "Saturday",  "slogan": "Little Warrior",                        "handle": "personalized-baby-pajama-born-on-saturday-little-warrior",                      "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-black-front-6a3963a7093a1.jpg"},
    {"day": "Sunday",    "slogan": "Favorite Day Got Better",               "handle": "personalized-baby-pajama-born-on-sunday-favorite-day-got-better",               "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-vintage-indigo-front-6a3965b815254.jpg"},
    {"day": "Sunday",    "slogan": "Humble and Happy",                      "handle": "personalized-baby-pajama-born-on-sunday-humble-and-happy",                      "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a396707b190c.jpg"},
    {"day": "Sunday",    "slogan": "Perfect Little Chaos",                  "handle": "personalized-baby-pajama-born-on-sunday-perfect-little-chaos",                  "img": "https://cdn.shopify.com/s/files/1/0786/1990/2279/files/baby-jersey-bodysuit-royal-front-6a3968058299e.jpg"},
]

TITLE_TEMPLATES = [
    "Born on a {day}? This is for them 🌙",
    "{day} baby gift — personalized bodysuit",
    "The perfect newborn gift for a {day} baby",
    "Your {day} baby will love this",
    "Born on {day} — customize with their name",
    "Baby shower gift for {day} babies",
]

DESC_TEMPLATES = [
    '"{slogan}" — personalized baby bodysuit for babies born on {day}. Add their birth name for a unique newborn gift they\'ll treasure. Perfect for baby showers! ✨\n\n👉 Customize at myweekdaybirth.com\n\n#{day_lower}baby #babygift #newborngift #babyshower #personalizedbaby #babybodysuit #babyshowergift #uniquebabygift',
    'A {day} baby is special — give them a gift that says so! "{slogan}" bodysuit, personalized with their birth name. 🌟\n\n→ myweekdaybirth.com\n\n#personalizedbaby #{day_lower}born #babygift #babyshower #newbornbodysuit #babygiftideas',
    'Born on {day}? "{slogan}" — the bodysuit that perfectly captures your little one. Customize with their name! 🎁\n\nmyweekdaybirth.com\n\n#{day_lower}baby #babyshowergift #newborngift #personalizedbodysuit #babygiftideas #uniquenewborngift',
]

STATE_FILE = "poster_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"boards": {}, "pins_posted_today": 0, "last_date": "", "product_index": 0, "variant_index": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_or_create_boards(state):
    """Fetch existing boards or create them."""
    if state.get("boards"):
        print(f"  Using {len(state['boards'])} existing boards")
        return state["boards"]

    print("  Fetching existing boards...")
    resp = requests.get(f"{BASE_URL}/boards", headers=HEADERS, params={"page_size": 100})
    existing = {b["name"]: b["id"] for b in resp.json().get("items", [])}

    boards = {}
    for key, name in BOARDS.items():
        if name in existing:
            boards[key] = existing[name]
            print(f"  ✓ Board exists: {name}")
        else:
            print(f"  + Creating board: {name}")
            r = requests.post(f"{BASE_URL}/boards", headers=HEADERS, json={
                "name": name,
                "privacy": "PUBLIC"
            })
            if r.status_code == 201:
                boards[key] = r.json()["id"]
            else:
                print(f"    Error: {r.text}")
            time.sleep(1)

    state["boards"] = boards
    save_state(state)
    return boards

def get_board_for_product(product, boards):
    """Pick appropriate board(s) for a product."""
    day = product["day"].lower()
    board_key = f"{day}_babies"
    selected = []
    if board_key in boards:
        selected.append(boards[board_key])
    if "baby_shower_gifts" in boards:
        selected.append(boards["baby_shower_gifts"])
    if "personalized_baby" in boards:
        selected.append(boards["personalized_baby"])
    return selected[:2]  # Post to max 2 boards

def post_pin(product, board_id, title_idx=0, desc_idx=0):
    """Post a single pin to Pinterest."""
    day = product["day"]
    slogan = product["slogan"]

    title = TITLE_TEMPLATES[title_idx % len(TITLE_TEMPLATES)].format(day=day)
    description = DESC_TEMPLATES[desc_idx % len(DESC_TEMPLATES)].format(
        slogan=slogan, day=day, day_lower=day.lower()
    )

    payload = {
        "board_id": board_id,
        "title": title[:100],  # Pinterest title limit
        "description": description[:500],
        "link": f"{SHOP_URL}{product['handle']}",
        "media_source": {
            "source_type": "image_url",
            "url": product["img"],
        },
    }

    resp = requests.post(f"{BASE_URL}/pins", headers=HEADERS, json=payload)

    if resp.status_code == 201:
        pin_id = resp.json().get("id", "?")
        print(f"  ✓ Pin posted: {title[:50]}... (id={pin_id})")
        return True
    else:
        print(f"  ✗ Failed ({resp.status_code}): {resp.text[:200]}")
        return False

def run_posting_session(pins_to_post=5):
    """Post a batch of pins. Called 3x/day by scheduled task."""
    if not PINTEREST_TOKEN:
        print("ERROR: PINTEREST_TOKEN not set")
        return

    state = load_state()
    today = date.today().isoformat()

    # Reset daily counter
    if state.get("last_date") != today:
        state["pins_posted_today"] = 0
        state["last_date"] = today

    print(f"\n📌 Pinterest poster — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   Pins today so far: {state['pins_posted_today']}")

    # Pinterest limit: 100 pins/day per user; we target 10-15/day
    if state["pins_posted_today"] >= 15:
        print("   Daily limit reached (15 pins). Skipping.")
        return

    boards = get_or_create_boards(state)
    if not boards:
        print("   No boards available. Exiting.")
        return

    posted = 0
    for _ in range(pins_to_post):
        if state["pins_posted_today"] >= 15:
            break

        product = PRODUCTS[state["product_index"] % len(PRODUCTS)]
        board_ids = get_board_for_product(product, boards)

        if board_ids:
            success = post_pin(
                product,
                board_ids[0],
                title_idx=state["variant_index"],
                desc_idx=state["variant_index"]
            )
            if success:
                posted += 1
                state["pins_posted_today"] += 1
                # Delay between pins to avoid rate limits
                time.sleep(random.uniform(3, 8))

        state["product_index"] = (state["product_index"] + 1) % len(PRODUCTS)
        state["variant_index"] = (state["variant_index"] + 1) % 6

    save_state(state)
    print(f"\n✅ Session done: {posted} pins posted (total today: {state['pins_posted_today']})")

if __name__ == "__main__":
    run_posting_session(pins_to_post=5)
