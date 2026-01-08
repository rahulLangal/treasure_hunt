import streamlit as st
import time
import datetime
import random

# --- App Configuration ---
# Check if the hunt is active or finished to collapse the sidebar
initial_sidebar_state = "expanded"
if "timer_running" in st.session_state and st.session_state.timer_running:
    initial_sidebar_state = "collapsed"
if "end_time" in st.session_state and st.session_state.end_time > 0:
    initial_sidebar_state = "collapsed"

st.set_page_config(
    page_title="DTSS College Treasure Hunt",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state=initial_sidebar_state
)

# --- Questions and Answers ---
QUESTIONS = {
    1: ("This is the first question. What is the answer?", "answer1"),
    2: ("This is the second question. What is the answer?", "answer2"),
    3: ("This is the third question. What is the answer?", "answer3"),
    4: ("This is the fourth question. What is the answer?", "answer4"),
    5: ("This is the fifth question. What is the answer?", "answer5"),
    6: ("This is the sixth question. What is the answer?", "answer6"),
}




# --- Initialize Session State ---
def init_session_state():
    """Initializes the session state variables if they don't exist."""
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = 0.0
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'end_time' not in st.session_state:
        st.session_state.end_time = 0.0
    if 'total_time_taken' not in st.session_state:
        st.session_state.total_time_taken = 0.0
    if 'question_order' not in st.session_state:
        st.session_state.question_order = []


# --- Main App Logic ---
def main():
    """Main function to run the Streamlit app."""
    init_session_state()

    st.markdown("<h1 style='text-align: center;'>DTSS College Treasure Hunt 🗺️</h1>", unsafe_allow_html=True)
    st.write("") # Spacer

    # Use timer_running as the primary state indicator for routing
    if st.session_state.total_time_taken > 0 or st.session_state.end_time > 0:
        handle_end_page()
    elif not st.session_state.timer_running:
        handle_start_page()
    elif st.session_state.current_question_index >= len(QUESTIONS):
        handle_end_page()
    else:
        # Explicit check to ensure we don't accidentally fall through if logic is complex
        handle_active_hunt()


def handle_start_page():
    """Renders the initial start page."""
    with st.container():
        st.subheader("Welcome, Treasure Hunter!")
        st.write(
            "Get ready for an exciting adventure across campus. "
            "Check the sidebar to start the timer and receive your first clue."
        )
        st.info("You will have **one hour** to complete the hunt. Good luck!", icon="⏳")
        
    # Move start button to sidebar
    with st.sidebar:
        st.header("Begin Adventure")
        if st.button("Start the Hunt! 🚀", key="start_button"):
            # Create a random order of questions for this session
            question_keys = list(QUESTIONS.keys())
            random.shuffle(question_keys)
            st.session_state.question_order = question_keys
            
            st.session_state.timer_running = True
            st.session_state.start_time = time.time()
            st.session_state.current_question_index = 0 # Start with the first question
            st.rerun()


def handle_active_hunt():
    """Handles the UI and logic when the hunt is active."""
    # Ensure current question index is valid
    if st.session_state.current_question_index >= len(QUESTIONS):
        handle_end_page()
        return # Exit to prevent further processing if hunt is effectively over

    # --- Timer and Progress Bar ---
    elapsed_time = time.time() - st.session_state.start_time
    if elapsed_time > 3600:  # 1 hour limit
        st.warning("Time's up! The hunt is over.")
        st.session_state.timer_running = False
        st.session_state.total_time_taken = 3600
        st.session_state.current_question_index = len(QUESTIONS) # Force to end page
        st.rerun() # Rerun to trigger end page
    
    timer_col, progress_col = st.columns(2)
    with timer_col:
        st.metric("Time Elapsed ⏳", format_time(elapsed_time))
    with progress_col:
        st.write("Your Progress:")
        st.progress((st.session_state.current_question_index) / len(QUESTIONS))

    st.write("---") # Divider

    # --- Question Display ---
    with st.container():
        # Get the current question number from the shuffled list
        q_index = st.session_state.current_question_index
        q_num = st.session_state.question_order[q_index]
        
        question, correct_answer = QUESTIONS[q_num]
        
        # Use the original question number for display if desired, or the step number
        st.subheader(f"Clue #{q_index + 1}")
        st.write(f"**{question}**")

        with st.form(key=f"question_{q_num}"):
            user_answer = st.text_input("Your Answer:", key=f"ans_{q_num}", placeholder="Type your answer here...")
            submit_button = st.form_submit_button("Submit Answer ➡️")

            if submit_button:
                if user_answer.strip().lower() == correct_answer.lower():
                    
                    st.session_state.current_question_index += 1
                    st.rerun()
                else:
                    st.error(" ")
    
    # Auto-refresh for timer
    if st.session_state.timer_running:
        time.sleep(1)
        st.rerun()


def handle_end_page():
    """Handles the UI and logic for the end of the hunt."""
    with st.container():
        st.subheader("🎉 This is the end! 🎉")
        st.markdown("**Please stop the timer only at the location instructed by the volunteers.**")
        
        if st.session_state.end_time == 0.0:
            if st.button("Stop Timer and See Your Result 🏁", key="stop_button"):
                st.session_state.end_time = time.time()
                st.session_state.timer_running = False
                st.session_state.total_time_taken = st.session_state.end_time - st.session_state.start_time
                st.rerun()
        else:
            st.balloons()
            st.success("Congratulations! You've completed the Treasure Hunt.")
            
            # Final Time Display
            st.metric("Your Total Time ⏱️", format_time(st.session_state.total_time_taken))
            
            if st.session_state.total_time_taken >= 3600:
                st.warning("You ran out of time, but great effort!")
            else:
                st.info("Well done on completing the hunt within the time limit!")


def format_time(seconds):
    """Formats seconds into a readable HH:MM:SS string."""
    return str(datetime.timedelta(seconds=int(seconds)))


if __name__ == "__main__":
    main()