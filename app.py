import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(page_title="What To Eat?", page_icon="🍳")

# --- SESSION STATE INITIALIZATION ---
# This keeps the profile data alive during the session but clears on refresh
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "dietary_pref": "",
        "allergies": "",
        "skill_level": "Beginner"
    }

st.title('What To Eat? || Recipe Recommendation System')

# Sidebar for API Key and Profile
st.sidebar.header("Settings & Profile")
google_api_key = st.sidebar.text_input('Google API Key', type='password')

# --- PROFILE SECTION ---
with st.sidebar.expander("👤 Edit Your Cooking Profile"):
    st.info("This info helps customize recipes but will be cleared if you refresh the page.")
    st.session_state.user_profile["name"] = st.text_input("Name", value=st.session_state.user_profile["name"])
    st.session_state.user_profile["dietary_pref"] = st.text_input("Dietary Preferences (e.g. Vegan, Keto)", value=st.session_state.user_profile["dietary_pref"])
    st.session_state.user_profile["allergies"] = st.text_input("Allergies", value=st.session_state.user_profile["allergies"])
    st.session_state.user_profile["skill_level"] = st.selectbox("Cooking Skill Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_profile["skill_level"]))

def generate_recommendations(ingredients):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # Updated to the latest stable flash model
            google_api_key=google_api_key,
            temperature=0.7
        )
        
        # Build Profile Context
        profile = st.session_state.user_profile
        profile_context = f"""
        User Context:
        - Dietary Preferences: {profile['dietary_pref']}
        - Allergies: {profile['allergies']}
        - Skill Level: {profile['skill_level']}
        """

        # Creating the enhanced prompt
        prompt = f"""
        {profile_context}
        
        Ingredients available: {ingredients}
        
        Please provide:
        1. **About the Dish**: A brief description (3-4 sentences) explaining what the food is, the combination of flavors, and the inspiration behind the dish.
        2. **Recipe**: An easy-to-cook, step-by-step recipe tailored to the user's profile and skill level.
        """
        
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# --- MAIN UI ---
if st.session_state.user_profile["name"]:
    st.subheader(f"Welcome back, {st.session_state.user_profile['name']}! 👋")

with st.form('recipe_form'):
    user_input = st.text_area('Enter your preferred ingredients (separated by commas):')
    submitted = st.form_submit_button('Get Recipe Recommendations')

if submitted:
    if not google_api_key:
        st.warning('Please enter your Google API Key in the sidebar.')
    elif not user_input:
        st.warning('Please list some ingredients first!')
    else:
        with st.spinner('The AI Chef is creating your personalized dish...'):
            recipe_data = generate_recommendations(user_input)
            if recipe_data:
                st.markdown("---")
                st.markdown(recipe_data)