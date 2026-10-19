import os
import sqlite3
from datetime import date, timedelta

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Smart Travel Planner",
    page_icon="✈️",
    layout="wide"
)

DB_NAME = "trips.db"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud").strip()
OLLAMA_URL = "https://ollama.com/api/chat"

# ---------------- DATABASE ----------------

def create_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                travelers INTEGER,
                budget REAL,
                interests TEXT,
                transport TEXT,
                accommodation TEXT,
                itinerary TEXT
            )
        """)

def save_trip(details, itinerary):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO trips (
                destination, start_date, end_date, travelers,
                budget, interests, transport, accommodation, itinerary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            details["destination"],
            str(details["start_date"]),
            str(details["end_date"]),
            details["travelers"],
            details["budget"],
            ", ".join(details["interests"]),
            details["transport"],
            details["accommodation"],
            itinerary
        ))

def get_saved_trips():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(
            "SELECT * FROM trips ORDER BY id DESC"
        ).fetchall()

create_database()

# ---------------- AI ITINERARY GENERATION ----------------

def create_fallback_plan(details):
    destination = details["destination"]
    start = details["start_date"]
    end = details["end_date"]
    days = (end - start).days + 1

    plan = [
        f"# Personalized Trip to {destination}",
        "",
        "This is a sample itinerary because the AI service "
        "is unavailable. Verify attractions, opening times, "
        "transport and prices before travelling.",
        "",
        f"**Travel dates:** {start} to {end}",
        f"**Travelers:** {details['travelers']}",
        f"**Total budget:** ₹{details['budget']:,.0f}",
        "",
        "## Suggested budget allocation",
        f"- Accommodation (30%): ₹{details['budget'] * 0.30:,.0f}",
        f"- Food (20%): ₹{details['budget'] * 0.20:,.0f}",
        f"- Transport (25%): ₹{details['budget'] * 0.25:,.0f}",
        f"- Activities (15%): ₹{details['budget'] * 0.15:,.0f}",
        f"- Emergency reserve (10%): ₹{details['budget'] * 0.10:,.0f}",
        "",
        "## Day-by-day plan"
    ]

    for i in range(days):
        current_date = start + timedelta(days=i)
        plan.extend([
            "",
            f"### Day {i + 1} — {current_date}",
            f"- Morning: Explore a well-known attraction in {destination}.",
            "- Afternoon: Enjoy local food and a nearby cultural or "
            "nature activity suited to your interests.",
            "- Evening: Explore a suitable public area and return "
            "to your accommodation.",
            "- Check local opening hours, travel times and costs in advance."
        ])

    plan.extend([
        "",
        "## Personalization",
        f"- Interests: {', '.join(details['interests']) or 'General sightseeing'}",
        f"- Transport preference: {details['transport']}",
        f"- Accommodation: {details['accommodation']}",
        "",
        "**Note:** This fallback is a general sample, not a verified "
        "recommendation for specific local attractions."
    ])

    return "\n".join(plan)


def generate_itinerary(details):
    prompt = f"""
Create a practical, personalized travel itinerary.

Destination: {details['destination']}
Start date: {details['start_date']}
End date: {details['end_date']}
Number of travelers: {details['travelers']}
Total trip budget in INR: {details['budget']}
Interests: {', '.join(details['interests'])}
Transport preference: {details['transport']}
Accommodation preference: {details['accommodation']}

Requirements:
1. Organize the itinerary day by day.
2. Suggest suitable morning, afternoon and evening activities.
3. Personalize recommendations to the stated interests.
4. Include an estimated budget breakdown in Indian rupees.
5. Include transport, accommodation and food suggestions.
6. Provide practical travel tips and safety advice.
7. Do not claim prices, opening hours, availability or facts are
   verified in real time.
8. Avoid exceeding the stated budget.
9. Mention when costs are estimates and suggest checking details.
10. Use clear Markdown headings and readable bullet points.
"""

    if not OLLAMA_API_KEY:
        raise ValueError(
            "OLLAMA_API_KEY is missing. Add it to your .env file."
        )

    response = requests.post(
        OLLAMA_URL,
        headers={
            "Authorization": f"Bearer {OLLAMA_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful travel-planning assistant. "
                        "Give realistic, budget-aware suggestions."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.5}
        },
        timeout=(15, 180)
    )

    if not response.ok:
        raise RuntimeError(
            f"Ollama API returned HTTP {response.status_code}: "
            f"{response.text[:500]}"
        )

    result = response.json()
    itinerary = result.get("message", {}).get("content", "").strip()

    if not itinerary:
        raise RuntimeError("The AI returned an empty itinerary.")

    return itinerary

# ---------------- SIDEBAR NAVIGATION ----------------

st.sidebar.title("✈️ Smart Travel Planner")
st.sidebar.write("AI-Powered Personalized Travel Assistant")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Plan My Trip", "Saved Trips"]
)

# ---------------- HOME PAGE ----------------

if page == "Home":
    st.title("✈️ Smart Travel Planner")
    st.subheader("Your AI-powered personalized travel companion")

    st.write(
        "Create customized travel itineraries based on your "
        "destination, dates, budget and interests."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🤖 AI Powered")
        st.write("Generate travel plans using Ollama AI.")

    with col2:
        st.subheader("🎯 Personalized")
        st.write("Customize plans to match your interests.")

    with col3:
        st.subheader("💰 Budget Friendly")
        st.write("Plan estimated expenses around your budget.")

    st.divider()
    st.subheader("How it works")
    st.write("1. Enter your destination and travel dates.")
    st.write("2. Select your budget, interests and preferences.")
    st.write("3. Generate your personalized itinerary.")
    st.write("4. Save and view your travel plans anytime.")

# ---------------- PLAN MY TRIP PAGE ----------------

elif page == "Plan My Trip":
    st.title("🗺️ Plan My Trip")
    st.write("Enter your preferences to create your travel itinerary.")

    with st.form("trip_form"):
        destination = st.text_input(
            "Destination",
            placeholder="Example: Goa, Hyderabad, Jaipur"
        )

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start date",
                value=date.today() + timedelta(days=7),
                min_value=date.today()
            )

        with col2:
            end_date = st.date_input(
                "End date",
                value=date.today() + timedelta(days=9),
                min_value=date.today()
            )

        travelers = st.number_input(
            "Number of travelers",
            min_value=1,
            max_value=20,
            value=2
        )

        budget = st.number_input(
            "Total budget (₹)",
            min_value=1000,
            max_value=10000000,
            value=40000,
            step=1000
        )

        interests = st.multiselect(
            "Your interests",
            [
                "Beaches", "Adventure", "Nature", "History",
                "Culture", "Food", "Shopping", "Photography",
                "Wildlife", "Relaxation", "Spiritual"
            ],
            default=["Nature", "Food"]
        )

        transport = st.selectbox(
            "Preferred transport",
            ["Flight", "Train", "Bus", "Car", "Public Transport"]
        )

        accommodation = st.selectbox(
            "Accommodation preference",
            ["Budget", "Standard", "Luxury"]
        )

        submitted = st.form_submit_button(
            "✨ Generate Travel Plan",
            use_container_width=True
        )

    if submitted:
        if not destination.strip():
            st.error("Please enter a destination.")
        elif end_date < start_date:
            st.error("End date must be on or after the start date.")
        else:
            details = {
                "destination": destination.strip(),
                "start_date": start_date,
                "end_date": end_date,
                "travelers": int(travelers),
                "budget": float(budget),
                "interests": interests,
                "transport": transport,
                "accommodation": accommodation
            }

            with st.spinner(
                "Creating your personalized itinerary. Please wait..."
            ):
                try:
                    itinerary = generate_itinerary(details)
                    st.session_state["itinerary"] = itinerary
                    st.session_state["trip_details"] = details
                    st.session_state["ai_generated"] = True

                except requests.exceptions.Timeout:
                    st.session_state["itinerary"] = create_fallback_plan(details)
                    st.session_state["trip_details"] = details
                    st.session_state["ai_generated"] = False
                    st.warning(
                        "The AI request timed out. Showing a sample "
                        "itinerary instead. Check your connection or "
                        "try again later for AI-generated recommendations."
                    )

                except Exception as exc:
                    st.session_state["itinerary"] = create_fallback_plan(details)
                    st.session_state["trip_details"] = details
                    st.session_state["ai_generated"] = False
                    st.error(f"AI generation failed: {exc}")
                    st.info(
                        "A sample itinerary is shown below. Check your "
                        "API key, model name and Ollama service."
                    )

    if st.session_state.get("itinerary"):
        st.divider()
        st.success("🎉 Your travel plan is ready!")
        st.markdown(st.session_state["itinerary"])

        details = st.session_state["trip_details"]

        if st.button("💾 Save This Trip", use_container_width=True):
            try:
                save_trip(details, st.session_state["itinerary"])
                st.success("Trip saved successfully!")
            except sqlite3.Error as exc:
                st.error(f"Could not save trip: {exc}")

        st.download_button(
            "📥 Download Itinerary",
            data=st.session_state["itinerary"],
            file_name="travel_itinerary.md",
            mime="text/markdown",
            use_container_width=True
        )

# ---------------- SAVED TRIPS PAGE ----------------

elif page == "Saved Trips":
    st.title("💾 Saved Trips")
    trips = get_saved_trips()

    if not trips:
        st.info("No saved trips yet. Generate and save a travel plan first.")
    else:
        st.write(f"Saved trips: {len(trips)}")

        for trip in trips:
            (
                trip_id, destination, start, end, travelers,
                budget, interests, transport, accommodation, itinerary
            ) = trip

            with st.expander(
                f"✈️ {destination} | {start} to {end}"
            ):
                st.write(f"**Travelers:** {travelers}")
                st.write(f"**Budget:** ₹{budget:,.0f}")
                st.write(f"**Interests:** {interests}")
                st.write(f"**Transport:** {transport}")
                st.write(f"**Accommodation:** {accommodation}")

                st.markdown(itinerary)

                st.download_button(
                    "Download this trip",
                    data=itinerary,
                    file_name=f"trip_{trip_id}.md",
                    mime="text/markdown",
                    key=f"download_{trip_id}"
                )

# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "Smart Travel Planner | AI-assisted itinerary planning. "
    "Verify travel information, costs and bookings independently."
)
