import streamlit as st
from datetime import date

from ai_planner import generate_itinerary
from database import create_tables, save_trip, get_trips


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Smart Travel Planner",
    page_icon="✈️",
    layout="wide"
)


# ==========================================
# DATABASE
# ==========================================

create_tables()


# ==========================================
# SESSION STATE
# ==========================================

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

if "trip_details" not in st.session_state:
    st.session_state.trip_details = None


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("✈️ Smart Travel Planner")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "🗺️ Plan My Trip",
        "💾 Saved Trips"
    ]
)


# ==========================================
# HOME
# ==========================================

if page == "🏠 Home":

    st.title("✈️ Smart Travel Planner")

    st.subheader(
        "AI-Powered Personalized Travel Planning Platform"
    )

    st.write("""
    Welcome to Smart Travel Planner!

    Enter your travel preferences and our AI will
    generate a personalized itinerary for you.
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("🤖 AI Powered")
        st.write(
            "AI-generated personalized travel plans."
        )

    with col2:
        st.success("🎯 Personalized")
        st.write(
            "Recommendations based on your interests."
        )

    with col3:
        st.warning("💰 Budget Friendly")
        st.write(
            "Plans based on your travel budget."
        )

    st.divider()

    st.subheader("How it works")

    st.write("""
    1. Enter your destination.
    2. Select your travel dates.
    3. Enter the number of travelers.
    4. Enter your budget.
    5. Select your interests.
    6. Choose transportation and accommodation.
    7. Click Generate AI Travel Plan.
    8. Save your generated trip.
    """)


# ==========================================
# PLAN MY TRIP
# ==========================================

elif page == "🗺️ Plan My Trip":

    st.title("🗺️ Plan My Trip")

    st.write(
        "Enter your preferences to generate your personalized trip."
    )

    st.divider()

    # ======================================
    # TRIP INFORMATION
    # ======================================

    st.subheader("📍 Trip Information")

    col1, col2 = st.columns(2)

    with col1:

        destination = st.text_input(
            "📍 Destination",
            placeholder="Example: Goa"
        )

        start_date = st.date_input(
            "📅 Start Date",
            value=date.today()
        )

        travelers = st.number_input(
            "👥 Number of Travelers",
            min_value=1,
            max_value=20,
            value=2,
            step=1
        )

        budget = st.number_input(
            "💰 Total Budget (₹)",
            min_value=1000,
            max_value=10000000,
            value=40000,
            step=1000
        )

    with col2:

        end_date = st.date_input(
            "📅 End Date",
            value=date.today()
        )

        transport = st.selectbox(
            "🚗 Transportation",
            [
                "Flight",
                "Train",
                "Bus",
                "Car",
                "Public Transport"
            ]
        )

        accommodation = st.selectbox(
            "🏨 Accommodation",
            [
                "Budget",
                "Standard",
                "Luxury"
            ]
        )

    # ======================================
    # INTERESTS
    # ======================================

    st.divider()

    st.subheader("❤️ Your Interests")

    interests = st.multiselect(
        "Select your interests",
        [
            "Beaches",
            "Adventure",
            "Nature",
            "History",
            "Culture",
            "Food",
            "Shopping",
            "Nightlife",
            "Photography",
            "Wildlife",
            "Relaxation",
            "Spiritual"
        ]
    )

    st.divider()

    # ======================================
    # GENERATE BUTTON
    # ======================================

    generate = st.button(
        "✨ Generate AI Travel Plan",
        type="primary",
        use_container_width=True
    )

    # ======================================
    # GENERATE AI PLAN
    # ======================================

    if generate:

        # ----------------------------------
        # VALIDATION
        # ----------------------------------

        if not destination.strip():

            st.error(
                "❌ Please enter a destination."
            )

        elif end_date < start_date:

            st.error(
                "❌ End date cannot be before start date."
            )

        elif travelers < 1:

            st.error(
                "❌ Number of travelers must be at least 1."
            )

        elif budget < 1000:

            st.error(
                "❌ Budget must be at least ₹1,000."
            )

        elif not interests:

            st.warning(
                "⚠️ Please select at least one interest."
            )

        else:

            with st.spinner(
                "🤖 AI is creating your personalized travel plan..."
            ):

                try:

                    # Convert interests list to text
                    interests_text = ", ".join(interests)

                    # Generate itinerary
                    itinerary = generate_itinerary(

                        destination=destination.strip(),

                        start_date=str(start_date),

                        end_date=str(end_date),

                        travelers=int(travelers),

                        budget=int(budget),

                        interests=interests_text,

                        transport=transport,

                        accommodation=accommodation
                    )

                    # ----------------------------------
                    # SAVE GENERATED PLAN IN SESSION
                    # ----------------------------------

                    st.session_state.itinerary = itinerary

                    st.session_state.trip_details = {

                        "destination": destination.strip(),

                        "start_date": str(start_date),

                        "end_date": str(end_date),

                        "travelers": int(travelers),

                        "budget": int(budget),

                        "interests": interests_text,

                        "transport": transport,

                        "accommodation": accommodation
                    }

                    st.success(
                        "🎉 Your travel plan has been generated!"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Error while generating plan: {e}"
                    )


    # ======================================
    # DISPLAY GENERATED ITINERARY
    # ======================================

    if st.session_state.itinerary:

        st.divider()

        st.header(
            "🧳 Your Personalized Travel Plan"
        )

        st.success(
            "Your AI-generated itinerary is ready!"
        )

        # Display AI output
        st.markdown(
            st.session_state.itinerary
        )

        st.divider()

        # ==================================
        # TRIP SUMMARY
        # ==================================

        if st.session_state.trip_details:

            details = st.session_state.trip_details

            st.subheader("📋 Trip Summary")

            summary_col1, summary_col2, summary_col3 = st.columns(3)

            with summary_col1:

                st.write(
                    f"**📍 Destination:** {details['destination']}"
                )

                st.write(
                    f"**📅 Dates:** "
                    f"{details['start_date']} → {details['end_date']}"
                )

                st.write(
                    f"**👥 Travelers:** {details['travelers']}"
                )

            with summary_col2:

                st.write(
                    f"**💰 Budget:** "
                    f"₹{details['budget']:,.0f}"
                )

                st.write(
                    f"**🚗 Transport:** {details['transport']}"
                )

                st.write(
                    f"**🏨 Accommodation:** "
                    f"{details['accommodation']}"
                )

            with summary_col3:

                st.write(
                    f"**❤️ Interests:** "
                    f"{details['interests']}"
                )

        st.divider()

        # ==================================
        # SAVE TRIP
        # ==================================

        st.subheader("💾 Save Your Trip")

        if st.button(
            "💾 Save This Trip",
            use_container_width=True
        ):

            try:

                details = st.session_state.trip_details

                save_trip(

                    destination=details["destination"],

                    start_date=details["start_date"],

                    end_date=details["end_date"],

                    travelers=details["travelers"],

                    budget=details["budget"],

                    interests=details["interests"],

                    transport=details["transport"],

                    accommodation=details["accommodation"],

                    itinerary=st.session_state.itinerary
                )

                st.success(
                    "✅ Trip saved successfully!"
                )

            except Exception as e:

                st.error(
                    f"❌ Error while saving trip: {e}"
                )


# ==========================================
# SAVED TRIPS
# ==========================================

elif page == "💾 Saved Trips":

    st.title("💾 Saved Trips")

    try:

        trips = get_trips()

    except Exception as e:

        st.error(
            f"❌ Error loading saved trips: {e}"
        )

        trips = []

    if not trips:

        st.info(
            "You don't have any saved trips yet."
        )

    else:

        for trip in trips:

            try:

                (
                    trip_id,
                    destination,
                    start_date,
                    end_date,
                    travelers,
                    budget,
                    interests,
                    transport,
                    accommodation,
                    itinerary
                ) = trip

            except ValueError:

                st.error(
                    "❌ Saved trip data format does not match the application."
                )

                break

            with st.expander(
                f"✈️ {destination} | "
                f"{start_date} → {end_date}"
            ):

                st.write(
                    f"**👥 Travelers:** {travelers}"
                )

                st.write(
                    f"**💰 Budget:** ₹{budget:,.0f}"
                )

                st.write(
                    f"**❤️ Interests:** {interests}"
                )

                st.write(
                    f"**🚗 Transport:** {transport}"
                )

                st.write(
                    f"**🏨 Accommodation:** {accommodation}"
                )

                st.divider()

                st.subheader("🧳 Itinerary")

                st.markdown(
                    itinerary
                )
